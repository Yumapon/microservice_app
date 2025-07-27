// 0〜5のステップで、どこまで進んでいるかを指定
const currentStep = 2;

window.addEventListener('DOMContentLoaded', () => {
  const nodes = document.querySelectorAll('.circuit .node');

  nodes.forEach((node, index) => {
    if (index <= currentStep) {
      node.classList.add('active');
    }
  });
});