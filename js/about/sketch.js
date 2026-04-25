
let imgArray = [];   // grows as images finish loading
let startPlaying = false;
let totalExpected = 0;
let c;

const CANVAS_W   = 600;
const CANVAS_H   = 338;
const PLAY_AFTER = 60;   // show sketch after this many images are ready

function setup() {
  c = createCanvas(CANVAS_W, CANVAS_H);
  c.parent('canvasContainer');
  pixelDensity(1);
  noStroke();
  loadJSON('js/about/wave600.json', onDataLoaded);
}

function onDataLoaded(data) {
  // Sort by distance from canvas centre so the most central images load first.
  // imgArray is populated progressively as each image finishes loading.
  let items = data.slice().sort(function(a, b) {
    return dist(a.x, a.y, CANVAS_W / 2, CANVAS_H / 2)
         - dist(b.x, b.y, CANVAS_W / 2, CANVAS_H / 2);
  });

  totalExpected = items.length;

  items.forEach(function(item) {
    var el = createImg(item.name, function() {
      el.size(CANVAS_W, CANVAS_H);
      el.hide();
      item.img = el;
      imgArray.push(item);
      if (imgArray.length === PLAY_AFTER) startPlaying = true;
    });
  });
}

function draw() {
  if (!startPlaying) {
    background(255);
    fill(180);
    noStroke();
    textSize(13);
    var pct = totalExpected ? floor(imgArray.length / totalExpected * 100) : 0;
    text('Loading ' + pct + '%', CANVAS_W / 2 - 32, CANVAS_H / 2);
    return;
  }

  // Find the item whose recorded position is closest to the cursor
  var minItem = imgArray[0];
  var minD    = dist(minItem.x, minItem.y, mouseX, mouseY);
  for (var i = 1; i < imgArray.length; i++) {
    var d = dist(imgArray[i].x, imgArray[i].y, mouseX, mouseY);
    if (d < minD) { minItem = imgArray[i]; minD = d; }
  }
  image(minItem.img, 0, 0, CANVAS_W, CANVAS_H);
}

function keyPressed() {
  if (key === 's') {
    var out = imgArray.map(function(item) {
      return { name: item.name, x: item.x, y: item.y };
    });
    saveJSON(out, 'wave600.json');
  } else if (key === 'l') {
    imgArray = [];
    startPlaying = false;
    loadJSON('js/about/wave600.json', onDataLoaded);
  }
}

function mousePressed() {
  console.log(mouseX, mouseY);
}
