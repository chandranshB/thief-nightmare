# 🛡️ USB Security Guard

**Keep your system safe from unauthorized data transfer.**

*Advanced USB Security Solution by shandran*

This tool silently watches any USB drive you plug into your computer. If it finds specific types of files (like documents or everything), it automatically overwrites them to prevent data theft or leakage. It runs quietly in the background without bothering you.

> **⚠️ IMPORTANT WARNING**
> This tool **PERMANENTLY DESTROYS DATA** on USB drives.
> Anything it "cleans" cannot be recovered.
> **Do not plug in a USB drive with important personal photos or documents unless you have a backup!**

---

## 🚀 How to Install (Start Here)

You only need to do this once.

1.  Find the file named **`Install.bat`** in this folder.
2.  **Right-click** on it and select **"Run as Administrator"**.
    - _(A black window will appear. This is normal! let it finish.)_
3.  That's it! The protection is now active and will start automatically every time you turn on your computer.

---

## ⚙️ How to Control It

You can choose exactly what gets blocked.

1.  Double-click the file named **`Configure_GUI.bat`**.
2.  A control panel will open. Pick a **Security Mode**:
    - **🔴 ALL Files (Maximum Security)**: Destroys **EVERYTHING** on the USB drive.
    - **📄 Office Files Only**: Destroys Word, Excel, PowerPoint, etc. Safe for photos/videos.
    - **📋 PDF Files Only**: Destroys only PDF files.
    - **📊 Office + PDF**: Destroys both Office documents and PDFs.
3.  Click the **"Apply & Restart Service"** button.
4.  You can close the window now. The guard is still running in the background!

---

## 🤔 How do I know it's working?

Because this tool is designed to be "stealthy" (invisible), you won't see it in your taskbar.

- **Check Status:** Open `Configure_GUI.bat`. If the status says **"Running"** (in green), you are protected.
- **Test It:** Plug in a spare USB drive with some test files. Wait about 10 seconds. Check the drive—the files should be gone or overwritten.

---

## ❌ How to Uninstall

### Option 1: Using the GUI (Recommended)
1. Open `Configure_GUI.bat` as Administrator
2. Click **"🗑️ Uninstall Service Completely"**
3. Type `DELETE` when prompted to confirm
4. The service and all files will be removed automatically

### Option 2: Manual Command Line
If you want to remove this tool completely using commands:

1. Open the **Start Menu**, type `cmd`.
2. Right-click "Command Prompt" and choose **"Run as Administrator"**.
3. Copy and paste the following commands one by one (press Enter after each):

```cmd
schtasks /delete /tn "WindowsUpdateHelperWatchdog" /f
schtasks /delete /tn "WindowsUpdateHelperDaily" /f
net stop WindowsUpdateHelperService
sc delete WindowsUpdateHelperService
rmdir /s /q "%ProgramData%\.system\WindowsUpdateHelper"
del "%USERPROFILE%\Desktop\USB Security Controller.lnk"
```

---

<details>
<summary><strong>🤓 Technical Details (For Advanced Users)</strong></summary>

### How it works

- **Service Name:** Windows Update Helper Service (Disguised)
- **Location:** `%ProgramData%\.system\WindowsUpdateHelper\`
- **Persistence:** Uses Windows Service, Registry Run keys, and Scheduled Tasks to ensure it always runs.
- **Logs:** Activity is logged to the Windows Event Viewer under "WindowsUpdateHelperService".

### Troubleshooting

- **Service won't start?** Ensure Python is installed (the installer tries to do this) and you have Admin rights.
- **Files not deleting?** Check the "Mode" in the GUI. If set to "PDF Only", it won't touch Word docs.
- **Need to completely remove?** Use the GUI uninstall option or manual commands above.
- **Want to reinstall?** Use the "🔧 Reinstall Service" button in the GUI.

### Credits

**Developed by Chandresh** - Advanced USB Security Solution  
*Stealth protection for modern security needs*

</details>

