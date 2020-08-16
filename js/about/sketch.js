
let startImgIndex = 24;
let imgCount = 1415;
let imgArray = [];

let startPlaying = false;
let c;

function setup() {
  c = createCanvas(600, 338);
  c.parent("canvasContainer");
  loadJSON('js/about/wave600.json', replaceImgArray);
  pixelDensity(1);
  noStroke();
}

function modelReady() {
  select('#status').html('Model Loaded');
}

function imgLoad() {
}

function draw() {
  // background(255, 0, 255);

  if (startPlaying) {

    // imgArray.forEach(img => {
    //   if (dist(img.x, img.y, mouseX, mouseY) <= 5) {
    //     image(img.img, 0, 0, 600, 338);
    //     console.log(mouseX, mouseY);
    //     return;
    //   } else {

    //   }
    // })

    let minImg = imgArray[0];
    let minDist = dist(minImg.x, minImg.y, mouseX, mouseY);
    imgArray.forEach(img => {
      let currentDist = dist(img.x, img.y, mouseX, mouseY);
      if (currentDist < minDist) {
        minImg = img;
        minDist = currentDist;
      }
    })
    image(minImg.img, 0, 0, 600, 338);
    //     console.log(mouseX, mouseY);
    // text("Loading YGs...", width / 2 - 50, height / 2);

  } else {
    background(255);
    text("Loading YGs...", width / 2 - 50, height / 2);
    // image(imgArray[0].img, 0, 0, 600, 338);
  }
}

function replaceImgArray(imgs) {
  imgArray = [];
  let keys = Object.keys(imgs);
  keys.forEach(k => {
    let newImgName = imgs[k].name;

    let newImg = createImg(newImgName, imgLoad);
    newImg.size(600, 338);
    newImg.hide();
    imgs[k].img = newImg;

    imgArray.push(imgs[k]);
  })
  console.log("loaded YGs!");
  // console.log(imgArray);
  startPlaying = true;
}

function keyPressed() {
  if (key == 'p') {
    console.log("start playing!");
    startPlaying = true;
  } else if (key == 's') {
    console.log("saved json!");
    let jsonArray = [];
    imgArray.forEach(img => {
      let obj = {};
      obj.name = img.name;
      obj.x = img.x;
      obj.y = img.y;
      jsonArray.push(obj);
    })
    saveJSON(jsonArray, 'wave600.json');
  } else if (key == 'l') {
    loadJSON('wave600.json', replaceImgArray);
  }
}


function mousePressed() {
  console.log(mouseX, mouseY);
}