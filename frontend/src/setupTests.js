import '@testing-library/jest-dom';

// Filter benign React Router v7 future flag notices and JSDOM canvas warnings in tests
const originalConsoleWarn = console.warn;
console.warn = (...args) => {
  if (typeof args[0] === 'string' && args[0].includes('React Router Future Flag Warning')) {
    return;
  }
  originalConsoleWarn(...args);
};

const originalConsoleError = console.error;
console.error = (...args) => {
  if (
    typeof args[0] === 'string' &&
    (args[0].includes("can't acquire context") || args[0].includes('Not implemented: HTMLCanvasElement'))
  ) {
    return;
  }
  originalConsoleError(...args);
};

// Mock HTMLCanvasElement.prototype.getContext for Chart.js in JSDOM
HTMLCanvasElement.prototype.getContext = () => ({
  fillRect: () => {},
  clearRect: () => {},
  getImageData: (x, y, w, h) => ({ data: new Array(w * h * 4) }),
  putImageData: () => {},
  createImageData: () => [],
  setTransform: () => {},
  drawImage: () => {},
  save: () => {},
  fillText: () => {},
  restore: () => {},
  beginPath: () => {},
  moveTo: () => {},
  lineTo: () => {},
  closePath: () => {},
  stroke: () => {},
  translate: () => {},
  scale: () => {},
  rotate: () => {},
  arc: () => {},
  fill: () => {},
  measureText: () => ({ width: 0 }),
  transform: () => {},
  resetTransform: () => {},
});
