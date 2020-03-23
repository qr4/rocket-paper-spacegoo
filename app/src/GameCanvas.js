import React, {useEffect, useRef, memo} from 'react';

let stars_buffer;
let planets_buffer;
let hyperlanes_buffer;
let last_gameId;

const default_shades = ["#BFBBB8", "#E4E0DC", "#807D7A", ];
const player1_shades = ["#00BF0A","#00E60B", "#004003"];
const player2_shades = ["#BF0020", "#E60028", "#800015",];

export const GameCanvas = memo(({turn, info, gameId}) => {
    let ref = useRef();

    useEffect(() => {
        if (!turn || !info || gameId === undefined) {
            return;
        }

        if (gameId !== last_gameId) {
           stars_buffer = null;
           planets_buffer = null;
           hyperlanes_buffer = null;
           last_gameId = gameId;
        }

        let canvas = ref.current;

        let width = getComputedStyle(canvas).getPropertyValue('width').slice(0, -2);
        let height = getComputedStyle(canvas).getPropertyValue('height').slice(0, -2);

        canvas.width = width;
        canvas.height = height;
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;

        const size_scale = 15;
        const planet_canvas_size = 50;
        const fleet_canvas_size = 5;
        const max_production = 18;
        const star_size = 4;

        // Off-screen canvas for stars
        if (!stars_buffer) {
            stars_buffer = document.createElement('canvas');
            stars_buffer.width = width;
            stars_buffer.height = height;
            const c = stars_buffer.getContext("2d");
            const n_stars = Math.floor(50 + Math.random()*50);
            for (let n = 0; n < n_stars; n++) {
                const x = Math.random()*width;
                const y = Math.random()*height;
                const r = Math.random() * star_size / 2;
                c.beginPath();
                c.fillStyle = "white";
                c.moveTo(x, y);
                c.arc(x, y, r, 0, 2*Math.PI, false);
                c.fill();
            }
        }


        // Off-screen canvas for planets
        if (!planets_buffer && turn && turn.planets) {
            planets_buffer = document.createElement('canvas');
            planets_buffer.width = width;
            planets_buffer.height = height;
            const bc = planets_buffer.getContext("2d");
            bc.translate(width/2, height/2);

            const planets = turn.planets;
            for (let idx = 0; idx < planets.length; idx++) {
                const planet = planets[idx];
                const total_production = planet.production[0] + planet.production[1] + planet.production[2];
                const r = Math.sqrt(total_production / (max_production*2)) * planet_canvas_size;
                let alpha = - Math.PI/2;
                for (let i = 0; i < 3; i++) {
                    const beta = alpha + 2 * Math.PI * (planet.production[i]/total_production);
                    bc.fillStyle = default_shades[i];
                    bc.beginPath();
                    bc.moveTo(
                        planet.x * -size_scale,
                        planet.y * size_scale
                    );
                    bc.arc(
                        planet.x * -size_scale,
                        planet.y * size_scale,
                        r,
                        alpha,
                        beta,
                        false
                    );
                    bc.closePath();
                    bc.fill();
                    alpha = beta;
                }
            }
        }

        if (!hyperlanes_buffer && turn && turn.hyperlanes) {
            hyperlanes_buffer = document.createElement('canvas');
            hyperlanes_buffer.width = width;
            hyperlanes_buffer.height = height;
            const hc = hyperlanes_buffer.getContext("2d");
            hc.translate(width/2, height/2);

            const planets = turn.planets;

            // remove duplicates
            const hyperlaneSet = new Set();
            const hyperlanes = turn.hyperlanes.filter(v => {
                const id1 = v[0] + "_" + v[1];
                const id2 = v[1] + "_" + v[0];
                if (hyperlaneSet.has(id1) || hyperlaneSet.has(id2))  {
                    return false;
                }
                hyperlaneSet.add(id1);
                hyperlaneSet.add(id2);
                return true;
            });

            for (let idx = 0; idx < hyperlanes.length; idx++) {
                const [start_idx, end_idx] = hyperlanes[idx];

                const pl1 = planets[start_idx];
                const pl2 = planets[end_idx];

                hc.save();
                hc.moveTo(pl1.x * -size_scale, pl1.y * size_scale);
                hc.lineTo(pl2.x * -size_scale, pl2.y * size_scale);
                hc.setLineDash([5, 20]);
                hc.strokeStyle = "lightgrey";
                hc.stroke();
                hc.restore();
            }
        }

        const render = () => {
            const c = canvas.getContext("2d");
            c.translate(width/2, height/2);

            c.clearRect(-canvas.width/2,-canvas.height/2,canvas.width,canvas.height);
            if (!turn || !turn.planets) return;

            c.drawImage(stars_buffer, -canvas.width/2, -canvas.height/2);
            c.drawImage(hyperlanes_buffer, -canvas.width/2, -canvas.height/2);

            const planets = turn.planets;
            for (let idx = 0; idx < planets.length; idx++) {
                const planet = planets[idx];
                const total_production = planet.production[0] + planet.production[1] + planet.production[2];
                const planet_r = Math.sqrt(total_production / (max_production*2)) * planet_canvas_size;

                // ship numbers per type
                for (let type = 0; type < 3; type++) {
                    const r = Math.log(planet.ships[type] / max_production + 1) * fleet_canvas_size + planet_r + 2;
                    c.beginPath();
                    c.fillStyle = [default_shades, player1_shades, player2_shades][planet.owner_id][type];
                    c.moveTo(
                        planet.x * -size_scale,
                        planet.y * size_scale
                    );
                    c.arc(
                        planet.x * -size_scale,
                        planet.y * size_scale,
                        r, Math.PI * (2/3 * type - 0.5), Math.PI * (2/3*(type+1) - 0.5), false);
                    c.fill();
                }

                // separator between ships and planet
                c.beginPath();
                c.fillStyle = "black";
                c.moveTo(
                    planet.x * -size_scale,
                    planet.y * size_scale
                );
                c.arc(
                    planet.x * -size_scale,
                    planet.y * size_scale,
                    planet_r + 2, 0, 2 * Math.PI, false);
                c.fill();
            }

            c.drawImage(planets_buffer, -canvas.width/2, -canvas.height/2);

            // semi-transparent planet owner overlay
            for (let idx = 0; idx < planets.length; idx++) {
                const planet = planets[idx];
                if (planet.owner_id !== 0) {
                    const total_production = planet.production[0] + planet.production[1] + planet.production[2];
                    const planet_r = Math.sqrt(total_production / (max_production*2)) * planet_canvas_size;
                    c.beginPath();

                    c.globalAlpha = 0.4;
                    c.fillStyle = ["lightgrey", "green", "red"][planet.owner_id];
                    c.moveTo(
                        planet.x * -size_scale,
                        planet.y * size_scale
                    );
                    c.arc(
                        planet.x * -size_scale,
                        planet.y * size_scale,
                        planet_r, 0, 2 * Math.PI, false);
                    c.fill();

                    c.globalAlpha = 1;
                    c.fillStyle = "#111111";
                    c.font = "bold 20px rps-font";
                    c.textAlign = "center";
                    c.textBaseline = "ideographic";
                    c.fillText(planet.production_rounds_left, planet.x * -size_scale, planet.y * size_scale + 10);

                }
            }
            c.globalAlpha = 1;

            const fleets = turn.fleets;
            for (let idx = 0; idx < fleets.length; idx++) {
                const fleet = fleets[idx];
                const total_ships = fleet.ships[0] + fleet.ships[1] + fleet.ships[2];
                if (total_ships === 0) {
                    continue;
                }

                const dx = planets[fleet.target].x - planets[fleet.origin].x;
                const dy = planets[fleet.target].y - planets[fleet.origin].y;
                const d = Math.ceil(Math.sqrt(dx * dx + dy * dy));
                const tl = (fleet.eta + 1) - turn.round;
                const done = 1 - (tl / d);
                const x = planets[fleet.origin].x + done * dx;
                const y = planets[fleet.origin].y + done * dy;
                const r = Math.sqrt(total_ships / (max_production*2)) * fleet_canvas_size;

                c.save();
                c.translate(x * -size_scale, y * size_scale);
                c.rotate(Math.atan2(dx,dy));

                // Triangle
                c.beginPath();
                c.fillStyle = ["invalid", "green", "red"][fleet.owner_id];
                c.moveTo(-(r+1),0);
                c.lineTo(0,2*r);
                c.lineTo( (r+1),0);
                c.closePath();
                c.fill();

                c.beginPath();
                c.moveTo(0,0);
                c.arc(0,0,r+1,Math.PI,0,false);
                c.closePath();
                c.fill();

                // Pie-Chart at the end
                let alpha = Math.PI;
                for (let i = 0; i < 3; i++) {
                    const beta = alpha + Math.PI * (fleet.ships[i]/total_ships);
                    c.fillStyle = default_shades[i];
                    c.beginPath();
                    c.moveTo(0,0);
                    c.arc(0,0,r,alpha,beta,false);
                    c.closePath();
                    c.fill();
                    alpha = beta;
                }
                c.restore();
            }

            // Last round
            if (turn.game_over) {
                let winner = turn.winner;
                if (!winner) {
                    winner = 0
                }
                c.fillStyle = ["lightgrey", player1_shades[1], player2_shades[1]][winner];
                c.font = "bold 60px rps-font";
                c.textAlign = "center";
                c.textBaseline = "ideographic";
                c.fillText([
                    "draw!",
                    info["player1"] + " wins!",
                    info["player2"] + " wins!"
                ][winner], 0, 0);
            }
        };

        render();
    });

    return (
            <canvas
                ref={ref}
                width={1316}
                height={500} />
    );
});