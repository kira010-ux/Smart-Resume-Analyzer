const { app, BrowserWindow } = require("electron");
const { spawn } = require("child_process");
const path = require("path");

let apiProcess;

function startApi() {
  const executable = path.join(process.resourcesPath, "backend-dist", "smart-resume-api.exe");
  if (!require("fs").existsSync(executable)) return;
  apiProcess = spawn(executable, [], { windowsHide: true });
}

function createWindow() {
  const window = new BrowserWindow({ width: 1240, height: 860, minWidth: 900, minHeight: 650, backgroundColor: "#f3f0e8" });
  window.loadFile(path.join(__dirname, "..", "dist", "index.html"));
}

app.whenReady().then(() => {
  startApi();
  createWindow();
  app.on("activate", () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});

app.on("window-all-closed", () => {
  if (apiProcess) apiProcess.kill();
  if (process.platform !== "darwin") app.quit();
});