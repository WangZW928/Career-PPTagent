import { applyDiagramToCanvas } from './excalidraw-utils';
import { exportToSvg, serializeAsJSON } from '@excalidraw/excalidraw';

window.exportDiagram = async (rendered) => {
  let elements = [];
  const api = {
    getSceneElements: () => elements,
    getSceneElementsIncludingDeleted: () => elements,
    updateScene: (scene) => { elements = scene.elements; },
    scrollToContent: () => {},
  };
  await applyDiagramToCanvas(api, rendered.skeletons, rendered.rawElements);
  const appState = { viewBackgroundColor: '#ffffff', exportBackground: true, exportWithDarkMode: false };
  const svg = await exportToSvg({ elements, appState, files: {}, exportPadding: 24 });
  return { svg: svg.outerHTML, scene: serializeAsJSON(elements, appState, {}, 'local'), count: elements.length };
};
