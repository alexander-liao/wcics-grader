function resize() {
  var size = Math.floor(Math.min(window.innerWidth, window.innerHeight) * 0.99);
  document.getElementById("canvas").width = size;
  document.getElementById("canvas").height = size;
}

resize();
window.onresize = resize;

function run(AI_A, AI_B) {
  var canvas = document.getElementById("canvas");
  var ctx = canvas.getContext("2d");
  
}