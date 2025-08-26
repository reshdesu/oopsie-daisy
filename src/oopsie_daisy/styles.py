def get_kitten_style() -> str:
    """
    Returns a sophisticated kitten-themed pink style using color theory principles:
    - Primary: Various shades of pink (warm, friendly, comforting)
    - Secondary: Soft purples and mauves (complementary to pink)
    - Accent: Warm whites and creams (creates contrast and breathing room)
    - Supporting: Soft grays and lavenders (neutral balance)
    
    Color Psychology: Pink promotes feelings of calm, nurturing, and safety - perfect
    for users who are stressed about losing files.
    """
    return """
    /* Force pink everywhere - Main window with sophisticated gradient background */
    QMainWindow {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #FFE4F0, stop:0.3 #FFD1E3, stop:0.7 #FFBDD6, stop:1 #FFA9C9);
        border: none;
    }
    
    /* Base widget styling - FORCE pink text everywhere */
    QWidget {
        background: transparent;
        font-family: 'Inter', 'Segoe UI', 'San Francisco', 'Helvetica Neue', sans-serif;
        font-size: 14px;
        color: #C2185B !important;
    }
    
    /* Override ANY system defaults */
    * {
        color: #C2185B !important;
        background-color: transparent;
    }
    
    /* SUPER PINK buttons - Qt compatible version */
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #FF1493, stop:0.5 #E91E63, stop:1 #C2185B);
        border: 5px solid #FF69B4;
        border-radius: 25px;
        color: #FFFFFF;
        font-weight: bold;
        font-size: 20px;
        padding: 18px 35px;
        min-width: 280px;
        min-height: 60px;
    }
    
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #FF69B4, stop:0.5 #FF1493, stop:1 #E91E63);
        border: 6px solid #FFB6C1;
        font-size: 22px;
    }
    
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #E91E63, stop:0.5 #C2185B, stop:1 #AD1457);
        border: 4px solid #FF1493;
        font-size: 18px;
    }
    
    QPushButton:disabled {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #E5E7EB, stop:1 #D1D5DB);
        border: 2px solid #F3F4F6;
        color: #9CA3AF;
    }
    
    /* Elegant label styling with hierarchy */
    QLabel {
        color: #831843;
        font-weight: 500;
        line-height: 1.5;
    }
    
    /* Title labels get special treatment */
    QLabel[objectName="title"] {
        color: #DB2777;
        font-weight: 700;
        font-size: 32px;
    }
    
    /* Subtitle styling */
    QLabel[objectName="subtitle"] {
        color: #BE185D;
        font-weight: 400;
        font-style: italic;
    }
    
    /* ULTRA PINK list widget - impossible to miss */
    QListWidget {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #FFE4F0, stop:1 #FFCCE5);
        border: 4px solid #FF1493;
        border-radius: 15px;
        padding: 15px;
        font-size: 16px;
        color: #C2185B !important;
        selection-background-color: #E91E63;
        selection-color: white !important;
        outline: none;
        font-weight: 600;
    }
    
    QListWidget::item {
        border: 1px solid #FBCFE8;
        border-radius: 8px;
        padding: 12px;
        margin: 3px 1px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(252, 231, 243, 0.6), stop:1 rgba(253, 242, 248, 0.6));
        font-weight: 500;
    }
    
    QListWidget::item:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #FFB6C1, stop:1 #FF69B4);
        border: 3px solid #FF1493;
        font-weight: bold;
    }
    
    QListWidget::item:selected {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #EC4899, stop:1 #DB2777);
        color: white;
        border: 2px solid #BE185D;
        font-weight: 600;
    }
    
    QListWidget::item:selected:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #DB2777, stop:1 #BE185D);
    }
    
    /* Elegant progress bar */
    QProgressBar {
        border: 2px solid #F9A8D4;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
        color: #831843;
        background: #FDF2F8;
        min-height: 20px;
    }
    
    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #F472B6, stop:0.3 #EC4899, stop:0.7 #DB2777, stop:1 #BE185D);
        border-radius: 10px;
        margin: 2px;
    }
    
    /* Refined scroll areas */
    QScrollArea {
        border: 1px solid #FBCFE8;
        border-radius: 10px;
        background: rgba(253, 242, 248, 0.9);
    }
    
    QScrollBar:vertical {
        background: #FDF2F8;
        width: 14px;
        border: 1px solid #FBCFE8;
        border-radius: 7px;
        margin: 0;
    }
    
    QScrollBar::handle:vertical {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #F472B6, stop:1 #EC4899);
        border-radius: 5px;
        min-height: 20px;
        margin: 2px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #EC4899, stop:1 #DB2777);
    }
    
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    /* Beautiful message boxes */
    QMessageBox {
        background: #FDF2F8;
        border: 2px solid #F9A8D4;
        border-radius: 12px;
    }
    
    QMessageBox QLabel {
        color: #831843;
        font-size: 14px;
        padding: 10px;
    }
    
    QMessageBox QPushButton {
        min-width: 100px;
        padding: 10px 20px;
        margin: 5px;
    }
    
    /* Success message styling - using complementary green */
    QMessageBox[iconPixmap*="information"] {
        border: 2px solid #86EFAC;
    }
    
    QMessageBox[iconPixmap*="information"] QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #86EFAC, stop:1 #4ADE80);
        border: 2px solid #22C55E;
        color: #14532D;
        font-weight: 600;
    }
    
    QMessageBox[iconPixmap*="information"] QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #4ADE80, stop:1 #22C55E);
    }
    
    /* Warning message styling - using analogous orange */
    QMessageBox[iconPixmap*="warning"] {
        border: 2px solid #FDBA74;
    }
    
    QMessageBox[iconPixmap*="warning"] QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #FDBA74, stop:1 #FB923C);
        border: 2px solid #EA580C;
        color: #9A3412;
        font-weight: 600;
    }
    
    QMessageBox[iconPixmap*="warning"] QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #FB923C, stop:1 #EA580C);
    }
    
    /* Tooltip styling */
    QToolTip {
        background: rgba(249, 168, 212, 0.95);
        border: 1px solid #F472B6;
        border-radius: 8px;
        color: #831843;
        font-size: 12px;
        padding: 8px 12px;
        font-weight: 500;
    }
    
    /* Focus indicators for accessibility */
    QPushButton:focus {
        outline: 2px solid #DB2777;
        outline-offset: 2px;
    }
    
    QListWidget:focus {
        border: 2px solid #DB2777;
    }
    """