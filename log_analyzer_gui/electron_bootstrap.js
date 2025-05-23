const { app, BrowserWindow } = require('electron');
const path = require('path');
const child_process = require('child_process');
const isDev = require('electron-is-dev');

let mainWindow;
let pythonEelProcess;

const pythonExecutable = process.platform === 'win32' ? 'python.exe' : 'python3';
let mainGuiPyPath;

if (isDev) {
    // In development, load directly from the project structure
    mainGuiPyPath = path.join(__dirname, 'main_gui.py');
} else {
    // In production (packaged app), it's an extraResource
    // It will be in 'resources/app/main_gui.py' relative to app root
    mainGuiPyPath = path.join(process.resourcesPath, 'app', 'main_gui.py');
}


function createWindow() {
    // Start the Python Eel process
    pythonEelProcess = child_process.spawn(pythonExecutable, [mainGuiPyPath], {
        stdio: ['pipe', 'pipe', 'pipe'] 
    });

    pythonEelProcess.stdout.on('data', (data) => {
        console.log(`Python stdout: ${data.toString()}`);
    });
    pythonEelProcess.stderr.on('data', (data) => {
        console.error(`Python stderr: ${data.toString()}`);
    });
    pythonEelProcess.on('error', (err) => {
        console.error('Failed to start Python process.', err);
    });
    pythonEelProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
    });


    mainWindow = new BrowserWindow({
        width: 850,
        height: 650,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
        }
    });

    let attempts = 0;
    function loadPage() {
        if (attempts < 20) { 
            mainWindow.loadURL('http://localhost:8000/main.html').then(() => {
                console.log("Page loaded successfully.");
            }).catch(err => {
                console.log("Failed to load URL, retrying...", err.message);
                setTimeout(loadPage, 500); 
                attempts++;
            });
        } else {
            console.error("Failed to load page after multiple attempts. Ensure Python Eel server is running.");
        }
    }
    
    setTimeout(loadPage, 2000); 

    if (isDev) {
        mainWindow.webContents.openDevTools(); 
    }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

app.on('quit', () => {
    console.log('Electron app quitting, killing Python process...');
    if (pythonEelProcess) {
        pythonEelProcess.kill();
    }
});
