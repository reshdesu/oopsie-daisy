# CI/CD Process for Oopsie Daisy

This document outlines the Continuous Integration and Continuous Deployment process for the Oopsie Daisy file recovery application.

## 🎯 **Quality Gates**

### **No Broken Releases Policy**
- **Releases are ONLY created if ALL tests pass**
- Build workflow depends on test success
- Failed tests = No release artifacts

## 🔄 **Workflow Overview**

### **1. Development Workflow (Push to Master)**
```
Push to master → Test Coverage Workflow
                ├─ Run 7 comprehensive tests
                ├─ Generate coverage reports  
                ├─ Upload artifacts
                └─ Report status ✅/❌
```

**Triggers on:**
- Push to `master`, `main`, `develop` branches
- Pull requests to `master`, `main`
- **Excludes**: Tag pushes (handled separately)

**What it does:**
- Runs full test suite with coverage
- Uploads HTML/XML coverage reports
- Provides fast feedback on code quality

### **2. Release Workflow (Create Tag)**
```
Create tag v* → Build and Release Workflow
                ├─ 1. Run Tests (Quality Gate) 🚪
                │   ├─ Platform detection
                │   ├─ Import verification
                │   ├─ Hardware monitoring
                │   └─ Basic functionality
                ├─ 2. Build (Only if tests pass)
                │   ├─ Windows executable
                │   ├─ macOS executable  
                │   └─ Linux executable
                └─ 3. Create Release
                    ├─ Upload executables
                    ├─ Generate release notes
                    └─ Publish on GitHub
```

**Triggers on:**
- Version tags (`v1.0.0`, `v2.1.2`, etc.)
- Manual workflow dispatch

**Quality Gate Process:**
1. **Tests MUST pass first** - No exceptions
2. If tests fail → Build jobs are skipped
3. If builds fail → No release is created
4. Only successful builds create releases

## ✅ **Test Suite**

### **Current Tests (7 total):**
1. **Python Version Check** - Ensures Python 3.12+
2. **Platform Detection** - Verifies Windows/macOS/Linux detection
3. **Module Imports** - Confirms all core modules load correctly
4. **Hardware Monitor Platform Detection** - Tests cross-platform logic
5. **Basic Functionality** - Validates core features work
6. **Main Function** - Ensures entry point works
7. **Main Function Exists** - Confirms callable main()

### **Test Coverage:**
- **Current**: ~17% code coverage
- **Growing**: New tests added regularly
- **Focus**: Core functionality and cross-platform compatibility

## 🚨 **Failure Handling**

### **If Tests Fail:**
- ❌ Build jobs are **automatically skipped**
- ❌ No executables are created
- ❌ No release is published
- 📧 GitHub sends failure notification
- 🔧 Developers must fix tests before release

### **If Builds Fail:**
- ❌ Release creation is **automatically skipped**
- ✅ Test artifacts are still available
- 📧 Build failure notifications sent
- 🔧 Build issues must be resolved

### **Debugging Failed Workflows:**
1. Check **Actions tab** in GitHub repository
2. Click on failed workflow run
3. Expand failed job to see error logs
4. Download test artifacts for local investigation
5. Fix issues and push/re-tag

## 📊 **Artifacts Created**

### **Development (Test Coverage Workflow):**
- `coverage-report/` - HTML coverage report
- `coverage.xml` - XML coverage for tools

### **Release (Build Workflow):**
- `oopsie-daisy-windows/OopsieDaisy.exe` - Windows executable
- `oopsie-daisy-macos/OopsieDaisy-macOS` - macOS executable  
- `oopsie-daisy-linux/OopsieDaisy-Linux` - Linux executable
- `test-results/coverage.xml` - Test results from quality gate

## 🎯 **Best Practices**

### **For Developers:**
1. **Run tests locally** before pushing: `uv run pytest`
2. **Check coverage**: `uv run pytest --cov=src/oopsie_daisy`
3. **Test cross-platform**: `uv run pytest tests/test_minimal.py`
4. **Only tag stable code** - Tests must pass locally first

### **For Releases:**
1. **Never skip failing tests** - Fix issues instead
2. **Use semantic versioning** - `v1.2.3` format  
3. **Review test results** before tagging
4. **Monitor workflow status** after tagging

## 🔧 **Workflow Files**

- **`.github/workflows/test-coverage.yml`** - Development testing
- **`.github/workflows/build-releases.yml`** - Release pipeline
- **`tests/test_minimal.py`** - Core test suite
- **`tests/test_init.py`** - Module initialization tests

## 📈 **Future Improvements**

- [ ] Increase test coverage to 50%+
- [ ] Add integration tests for file recovery
- [ ] Add performance benchmarks
- [ ] Implement automatic dependency updates
- [ ] Add security scanning
- [ ] Create staging environment testing

---

**Remember**: This process ensures **zero broken releases** reach users. Quality gates protect our reputation! 🛡️