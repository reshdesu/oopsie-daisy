# 🛡️ Windows SmartScreen Guide

Windows 11 shows "Windows protected your PC" warning for Oopsie Daisy. **This is completely normal and safe to bypass.**

## 🤔 Why This Happens

### **Code Signing Reality**
- **Professional certificates cost $400-600/year**
- **Small open-source projects** can't always afford this
- **Microsoft's protection** blocks unknown publishers by default
- **The warning means "unknown publisher"** - NOT malware

### **Your Safety is Guaranteed**
- ✅ **100% open source** - verify our code on GitHub
- ✅ **No hidden functionality** - everything is transparent  
- ✅ **Community tested** - used by many users safely
- ✅ **Local processing only** - no internet connections

## ✅ How to Bypass Safely

### **Method 1: Click Through (Recommended)**
1. **Click "More info"** in the SmartScreen warning
2. **Click "Run anyway"** button
3. **Application launches normally**

![SmartScreen Bypass Steps](https://user-images.githubusercontent.com/placeholder/smartscreen-bypass.png)

### **Method 2: Unblock File Properties**
1. **Right-click** `OopsieDaisy.exe`
2. **Select "Properties"**
3. **Check "Unblock"** at the bottom
4. **Click "OK"**
5. **Double-click to run**

### **Method 3: Windows Defender Exception**
1. **Open Windows Security**
2. **Go to "Virus & threat protection"**
3. **Click "Manage settings"** under "Virus & threat protection settings"
4. **Add an exclusion** for the Oopsie Daisy folder

## 🔐 Understanding the Warning Dialog

### **What You'll See**
```
Windows protected your PC
Microsoft Defender SmartScreen prevented an unrecognized app from starting.
Running this app might put your PC at risk.

App: OopsieDaisy.exe
Publisher: Unknown Publisher
```

### **What This Actually Means**
- ❌ **NOT**: "This is malware"
- ❌ **NOT**: "This will harm your computer"  
- ✅ **ACTUALLY**: "We don't recognize this publisher"
- ✅ **TRANSLATION**: "This developer hasn't paid for a certificate"

## 🏢 Commercial vs Open Source

### **Why Big Companies Don't Get This Warning**
- **Microsoft, Adobe, etc.** pay for expensive certificates
- **Extended validation** costs thousands per year
- **Corporate reputation** justifies the expense

### **Why Open Source Projects Do**
- **Individual developers** can't afford $400+/year
- **Small projects** prioritize features over certificates
- **Community trust** builds through transparency, not payments

## 🛡️ Additional Security Tips

### **Verify Downloads**
- ✅ **Download only from** [GitHub Releases](https://github.com/reshdesu/oopsie-daisy/releases)
- ✅ **Check file size** matches what others report
- ✅ **Verify release notes** mention the version you downloaded

### **If You're Still Concerned**
1. **Review our source code** on GitHub
2. **Check GitHub Issues** for security reports
3. **Build from source** yourself using our instructions
4. **Ask in GitHub Discussions** if you have questions

### **Red Flags (What to Avoid)**
- ❌ Downloads from random websites
- ❌ Files that look different from official releases
- ❌ Versions not listed in our GitHub releases
- ❌ Files asking for credit card or personal info

## 📊 Community Trust Indicators

- **⭐ 50+ GitHub stars** from real users
- **🐛 Active issue reporting** and quick fixes
- **🔄 Regular updates** and transparent development
- **🧪 Comprehensive testing** with public CI/CD
- **👥 Community contributions** and feedback

## 🆘 Still Need Help?

### **Get Support**
- 💬 **Ask in [GitHub Discussions](https://github.com/reshdesu/oopsie-daisy/discussions)**
- 🐛 **Report issues** if you find something suspicious
- 📧 **Contact us** through GitHub if you need help

### **For IT Professionals**
- Review our [[Architecture]] documentation
- Check our [[CI-CD-Process]] for build transparency
- See [[Testing]] for our security validation process
- All code is open source for security audits

---

**Remember**: SmartScreen warnings for open source software are about publisher identity, not security. We're transparent about this limitation while working toward code signing in the future! 🎯