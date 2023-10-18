(ns rps
  (:require [clj-sockets.core :as s]
            [clojure.pprint :refer [pprint]]
            [clojure.data.json :as json]
            [clojure.string :as str])
  (:gen-class))

(def ^:private user-name "<PICK_AN_USER_NAME>")
(def ^:private password  "<PICK_A_PASSWORD>")

(def ^:private socket
  (s/create-socket "rps.qr4.dev" 6000))

(defn- write [s]
  (println "SENDING" s)
  (s/write-line socket s))

(defn- login [socket]
  (write (format "login %s %s" user-name password)))

;; only an asymetric round. this needs to be called twice
(defn- battle-round [attacker defender]
  (let [num-ships (count attacker)]
    (map-indexed (fn [defender-idx defender-count]
                   (loop [total-loss 0
                          cur-attacker-idx 0]
                     (if (>= cur-attacker-idx num-ships)
                       (max 0 (- defender-count total-loss))

                       (let [attacker-count (nth attacker cur-attacker-idx)
                             [multiplier absolute-loss]
                             (cond
                               (= defender-idx cur-attacker-idx)                       [0.1  1]
                               (= 1 (mod (- defender-idx cur-attacker-idx) num-ships)) [0.25 2]
                               (= (- num-ships 1)
                                  (mod (- defender-idx cur-attacker-idx) num-ships))   [0.01 1])]
                         (recur
                          (+ total-loss
                             (max (* attacker-count multiplier)
                                  (* (if (> attacker-count 0) 1 0)
                                     absolute-loss)))
                          (inc cur-attacker-idx))))))
                 defender)))

;; simulates a battle of two fleets `s1` and `s2`.
;; returns the surviving ships of each fleet after the battle
;; Note: One of the fleet will always be eliminated
(defn- battle [s1 s2]
  (loop [s1 s1
         s2 s2]
    (if (or (= 0 (apply + s1))
            (= 0 (apply + s2)))
      [(map int s1)
       (map int s2)]
      (recur (battle-round s2 s1)
             (battle-round s1 s2)))))

(defn- process-game-state [{:keys [player_id
                                   winner
                                   planets
                                   game_over]
                            :as d}]
  #_(pprint d)
  (if (or (some? winner)
          (true? game_over))
    (println "Game Over.")

    ;; very simple approach: Find planet under our control which has the most ships
    ;; and send 1/6 of each to a random planet which is _not_ under our control.
    (let [enemy-planets (filter #(not= (:owner_id %) player_id) planets)
          my-planets (filter #(= (:owner_id %) player_id) planets)
          my-planet-with-most-ships (->> my-planets
                                         (sort-by #(apply + (:ships %)))
                                         last)
          target-planet (when (seq enemy-planets)
                          (rand-nth enemy-planets))]
      (if (and
           (some? my-planet-with-most-ships)
           (some? target-planet))
        (write (format "send %s %s %d %d %d"
                       (:id my-planet-with-most-ships)
                       (:id target-planet)
                       (-> my-planet-with-most-ships
                           :ships
                           (nth 0)
                           (/ 6)
                           int)
                       (-> my-planet-with-most-ships
                           :ships
                           (nth 1)
                           (/ 6)
                           int)
                       (-> my-planet-with-most-ships
                           :ships
                           (nth 2)
                           (/ 6)
                           int)))
        (write "nop")))))

(defn -main
  "Invoke me with `clojure -M -m rps` or `clojure -M:run`"
  [& args]
  (login socket)
  (let [game-finished? (atom false)]
    (while (not @game-finished?)
      (let [d (-> socket
                  (s/read-line))]
        (cond
          (nil? d) (reset! game-finished? true)
          (str/starts-with? d "game is over") (reset! game-finished? true)
          (not (str/starts-with? d "{")) (println d)
          :else (process-game-state (json/read-str d :key-fn keyword)))))))
