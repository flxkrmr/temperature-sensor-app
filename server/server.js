const express = require('express')
const pug = require('pug')
const path = require("path")
const fs = require('fs')

const app = express()
const port = 80
const measurementsFolder = '../measurements/'
const settingsFile = '../settings.json'
const bodyParser = require('body-parser')

app.use( bodyParser.json() );       // to support JSON-encoded bodies
app.use(bodyParser.urlencoded({     // to support URL-encoded bodies
  extended: true
})); 

app.set("views", path.join(__dirname, "views"));
app.set("view engine", "pug");
app.use(express.static(path.join(__dirname, "public")));

app.use("/measurements", express.static(path.join(__dirname, "../measurements")));

app.get('/', (req, res) => {
  measurementsFiles = []
  fs.readdirSync(measurementsFolder).forEach(file => {
    measurementsFiles.push(file)
  });
  
  var settings = JSON.parse(fs.readFileSync(settingsFile));

  res.render("index", { 
    title: "Home",
    files: measurementsFiles,
    measuring: settings['measuring']
  });
})

app.get('/stop', (req, res) => {
  var settings = JSON.parse(fs.readFileSync(settingsFile));

  res.render("stop", { 
    title: "Stop",
    measuring: settings['measuring']
  });
})

app.post('/stop', (req, res) => {
  var settings = JSON.parse(fs.readFileSync(settingsFile));
  settings['measuring'] = false;

  fs.writeFileSync(settingsFile, JSON.stringify(settings, null, 4));

  res.redirect("/");
})

app.get('/start', (req, res) => {
  var settings = JSON.parse(fs.readFileSync(settingsFile));

  res.render("start", { 
    title: "Start",
    measuringfilename: settings['fileName'],
    measuring: settings['measuring'],
    interval: settings['intervalSeconds']
  });
})

app.post('/start', (req, res) => {
  var settings = JSON.parse(fs.readFileSync(settingsFile));
  settings['measuring'] = true,
  settings['fileName'] = req.body.filename,
  settings['intervalSeconds'] = parseInt(req.body.interval, 10),

  fs.writeFileSync(settingsFile, JSON.stringify(settings, null, 4));

  res.redirect("/");
})

app.get('/delete/:filename', (req, res) => {
  res.render("delete", { 
    title: "Löschen",
    measuringFilename: req.params.filename
  });
})

app.post('/delete/:filename', (req, res) => {
  console.log(measurementsFolder + req.params.filename);
  // I think this is evil!
  fs.unlinkSync(measurementsFolder + req.params.filename);
  res.redirect("/");
})

app.listen(port, () => {
  console.log(`App listening on port ${port}`)
})
