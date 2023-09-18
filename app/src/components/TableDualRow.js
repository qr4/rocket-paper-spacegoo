// NOTE (LinuCC) Copied from arwes

import { withStyles } from '@arwes/arwes';
import AnimationComponent from '@arwes/arwes/lib/Animation';
import React from 'react';
import cx from 'classnames';
import styles from '@arwes/arwes/lib/Table/styles';

const Table = withStyles(styles)((props) => {
  const {
    theme,
    classes,
    Animation,
    animation,
    animate,
    show,
    headers,
    dataset,
    minWidth,
    className,
    children,
    ...etc
  } = props;
  const cls = cx(classes.root, className);

  return (
    <Animation
      animate={animate}
      show={show}
      timeout={theme.animTime}
      {...animation}
    >
      {anim => (
        <div className={cx(cls, classes[anim.status])} {...etc}>
          <div style={{ minWidth }}>
            {!children && (
              <table>
                <thead>
                  <tr>
                    {headers[0].map((header, index) => (
                      <th key={index}>{header}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr>
                  {dataset[0].map((item, index) => (
                    <td key={index}>{item}</td>
                  ))}
                  </tr>
              </tbody>
                <thead>
                  <tr>
                    {headers[1].map((header, index) => (
                      <th key={index}>{header}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr>
                  {dataset[1].map((item, index) => (
                    <td key={index}>{item}</td>
                  ))}
                  </tr>
              </tbody>
              </table>
            )}
            {children}
          </div>
        </div>
      )}
    </Animation>
  );
});

// Table.propTypes = {
//   Animation: PropTypes.any.isRequired,
//
//   theme: PropTypes.any.isRequired,
//   classes: PropTypes.any.isRequired,
//
//   animate: PropTypes.bool,
//   show: PropTypes.bool,
//   animation: PropTypes.object,
//
//   /**
//    * List of heading titles.
//    */
//   headers: PropTypes.array,
//
//   /**
//    * List of rows with their lists of columns.
//    */
//   dataset: PropTypes.arrayOf(PropTypes.array),
//
//   /**
//    * The table component can be the 100% width container.
//    * Configure the min width of the content, if case the container width is less
//    * than this minWidth, a horizontal scroll will appear.
//    */
//   minWidth: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
//
//   /**
//    * If the actual HTML `<table />` is provided, the `headers` and `dataset`
//    * are ignored.
//    */
//   children: PropTypes.any,
//
//   className: PropTypes.any
// };

Table.defaultProps = {
  Animation: AnimationComponent,
  show: true,
  headers: [],
  dataset: []
};

  export default Table;
