# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'query_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFormLayout,
    QGridLayout, QHBoxLayout, QLabel, QLayout,
    QPushButton, QSizePolicy, QTextEdit, QVBoxLayout,
    QWidget)
from . import resources_rc

class Ui_Edit_Query_Dialog(object):
    def setupUi(self, Edit_Query_Dialog):
        if not Edit_Query_Dialog.objectName():
            Edit_Query_Dialog.setObjectName(u"Edit_Query_Dialog")
        Edit_Query_Dialog.setEnabled(True)
        Edit_Query_Dialog.resize(536, 933)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Edit_Query_Dialog.sizePolicy().hasHeightForWidth())
        Edit_Query_Dialog.setSizePolicy(sizePolicy)
        Edit_Query_Dialog.setMinimumSize(QSize(0, 0))
        Edit_Query_Dialog.setMaximumSize(QSize(16777215, 16777215))
        Edit_Query_Dialog.setStyleSheet(u"QDialog {\n"
"    background-color: #011C26; \n"
"}\n"
"\n"
"QWidget {	\n"
"	font: 13pt \"Helvetica\";\n"
"    color: #F9F9F9;\n"
"}\n"
"\n"
"QLabel[class=label] {	\n"
"	font: 10pt;\n"
"    color: #F9F9F9;\n"
"}\n"
"\n"
"QWidget[class=container] {	\n"
"    background: #042F40;\n"
"	border-radius: 10px\n"
"}\n"
"\n"
"QLabel[class=hint] {\n"
"	color: #799582;\n"
"}\n"
"\n"
"QLabel[class=title] {\n"
"	font: 700 24pt;\n"
"}\n"
"\n"
"QLineEdit, QTextEdit{\n"
"	background-color: #011C26;\n"
"	border: none;\n"
"	border-radius: 6px;\n"
"	\n"
"}\n"
"\n"
"/* --- Main Box --- */\n"
"QComboBox {\n"
"    background-color: #011C26;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 5px 10px;\n"
"    color: #F9F9F9;\n"
"    /* This helps selection color in some styles */\n"
"    selection-background-color: #011C26; \n"
"}\n"
"\n"
"/* --- The Dropdown Frame --- */\n"
"/* We target QListView specifically to override Mac defaults */\n"
"QComboBox QListView {\n"
"    background-color: #011C26;\n"
"    border: 1px"
                        " solid #042F40; /* Your custom border */\n"
"    outline: 0px; /* Removes the dotted/blue focus line */\n"
"    padding: 0px;\n"
"}\n"
"\n"
"\n"
"\n"
"/* --- The Arrow Button Area --- */\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 24px;\n"
"    border-left: 1px solid #042F40; /* Optional: adds a separator */\n"
"    border-top-right-radius: 6px;\n"
"    border-bottom-right-radius: 6px;\n"
"}\n"
"\n"
"QComboBox::down-arrow {\n"
"    image: url(:/icons/icons/down.svg);\n"
"    width: 10px;\n"
"    height: 10px;\n"
"}\n"
"\n"
"/* --- Main Spinbox Styling (Applies to both) --- */\n"
"QSpinBox, QDoubleSpinBox {\n"
"    background-color: #011C26;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    color: #F9F9F9;\n"
"    padding: 5px 10px;\n"
"    padding-right: 15px; \n"
"}\n"
"\n"
"/* --- The Button Container Areas --- */\n"
"QSpinBox::up-button, QDoubleSpinBox::up-button {\n"
"    subcontrol-origin: border;\n"
"    subcontrol-position"
                        ": top right;\n"
"    width: 25px;\n"
"    \n"
"    border-left: 1px solid #042F40;\n"
"    border-top-right-radius: 6px;\n"
"    border-bottom: 1px solid #042F40;\n"
"    \n"
"    background-color: #011C26;\n"
"}\n"
"\n"
"QSpinBox::down-button, QDoubleSpinBox::down-button {\n"
"    subcontrol-origin: border;\n"
"    subcontrol-position: bottom right;\n"
"    width: 25px;\n"
"    \n"
"    border-left: 1px solid #042F40;\n"
"    border-bottom-right-radius: 6px;\n"
"    \n"
"    background-color: #011C26;\n"
"}\n"
"\n"
"/* --- Hover Effects --- */\n"
"QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,\n"
"QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover, QComboBox::drop-down:hover {\n"
"    background-color: #042F40;\n"
"}\n"
"\n"
"/* --- The Arrow Icons --- */\n"
"/* (Assuming you are using the CSS Arrow hack from before. \n"
"   If using images, replace these with your image: url(...) code) */\n"
"\n"
"QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {\n"
"    image: url(:/icons/icons/up.svg)"
                        "; /* You need to create this file */\n"
"    width: 10px;\n"
"    height: 10px;\n"
"}\n"
"\n"
"QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {\n"
"    image: url(:/icons/icons/down.svg); /* You need to create this file */\n"
"    width: 10px;\n"
"    height: 10px;\n"
"}\n"
"\n"
"QToolButton {\n"
"    background-color: #032F40; \n"
"    border-radius: 16px;       \n"
"    border: none;\n"
"    text-align: center;\n"
"}\n"
"\n"
"QToolButton:hover {\n"
"    background-color: #314250; \n"
"}\n"
"\n"
"QToolButton:pressed {\n"
"    background-color: #032F40;\n"
"}\n"
"\n"
"QPushButton {\n"
"	color: #011C26;\n"
"	border-radius: 16px\n"
"}\n"
"\n"
"QPushButton#b_save {\n"
"	background-color: #799582\n"
"}\n"
"QPushButton#b_save:hover {\n"
"    background-color: rgb(155, 191, 168); \n"
"}\n"
"QPushButton#b_save:pressed {\n"
"    background-color: #799582; \n"
"}\n"
"\n"
"QPushButton#b_delete {\n"
"	background-color: #042F40;\n"
"	color: #F9F9F9;\n"
"}\n"
"\n"
"QPushButton#b_delete:hover {\n"
"    background-color: #"
                        "314250; \n"
"}\n"
"QPushButton#b_delete:pressed {\n"
"    background-color: #042F40; \n"
"}")
        self.verticalLayout = QVBoxLayout(Edit_Query_Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.widget = QWidget(Edit_Query_Dialog)
        self.widget.setObjectName(u"widget")
        self.General = QVBoxLayout(self.widget)
        self.General.setSpacing(0)
        self.General.setObjectName(u"General")
        self.General.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.General.setContentsMargins(0, 8, 0, 0)
        self.widget_3 = QWidget(self.widget)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout = QHBoxLayout(self.widget_3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(8, 0, 0, 4)
        self.label_2 = QLabel(self.widget_3)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMargin(0)

        self.horizontalLayout.addWidget(self.label_2)


        self.General.addWidget(self.widget_3, 0, Qt.AlignmentFlag.AlignLeft)

        self.widget1 = QWidget(self.widget)
        self.widget1.setObjectName(u"widget1")
        self.widget1.setMinimumSize(QSize(0, 80))
        self.gridLayout = QGridLayout(self.widget1)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(4)
        self.gridLayout.setVerticalSpacing(8)
        self.gridLayout.setContentsMargins(8, 4, 4, 4)
        self.l_preview = QLabel(self.widget1)
        self.l_preview.setObjectName(u"l_preview")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.l_preview.sizePolicy().hasHeightForWidth())
        self.l_preview.setSizePolicy(sizePolicy1)
        self.l_preview.setMinimumSize(QSize(500, 100))
        self.l_preview.setMaximumSize(QSize(500, 16777215))
        self.l_preview.setScaledContents(False)
        self.l_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.l_preview.setWordWrap(True)

        self.gridLayout.addWidget(self.l_preview, 0, 0, 1, 1)


        self.General.addWidget(self.widget1)


        self.verticalLayout.addWidget(self.widget)

        self.widget_4 = QWidget(Edit_Query_Dialog)
        self.widget_4.setObjectName(u"widget_4")
        self.General_2 = QVBoxLayout(self.widget_4)
        self.General_2.setSpacing(0)
        self.General_2.setObjectName(u"General_2")
        self.General_2.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.General_2.setContentsMargins(0, 0, 0, 0)
        self.widget_5 = QWidget(self.widget_4)
        self.widget_5.setObjectName(u"widget_5")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(8, 0, 0, 4)
        self.label_4 = QLabel(self.widget_5)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMargin(0)

        self.horizontalLayout_3.addWidget(self.label_4)


        self.General_2.addWidget(self.widget_5, 0, Qt.AlignmentFlag.AlignLeft)

        self.widget_6 = QWidget(self.widget_4)
        self.widget_6.setObjectName(u"widget_6")
        self.formLayout = QFormLayout(self.widget_6)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.formLayout.setFormAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.formLayout.setHorizontalSpacing(8)
        self.formLayout.setVerticalSpacing(8)
        self.label_14 = QLabel(self.widget_6)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.label_14.setMargin(0)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_14)

        self.d_car = QComboBox(self.widget_6)
        self.d_car.setObjectName(u"d_car")
        self.d_car.setMinimumSize(QSize(0, 24))
        self.d_car.setMaximumSize(QSize(16777215, 24))
        self.d_car.setFrame(False)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.d_car)

        self.label_32 = QLabel(self.widget_6)
        self.label_32.setObjectName(u"label_32")
        self.label_32.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.label_32.setMargin(0)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_32)

        self.t_umlsl = QTextEdit(self.widget_6)
        self.t_umlsl.setObjectName(u"t_umlsl")
        self.t_umlsl.setMinimumSize(QSize(0, 100))
        self.t_umlsl.setMaximumSize(QSize(16777215, 1000))

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.t_umlsl)


        self.General_2.addWidget(self.widget_6)


        self.verticalLayout.addWidget(self.widget_4)

        self.widget2 = QWidget(Edit_Query_Dialog)
        self.widget2.setObjectName(u"widget2")
        self.Lanes = QVBoxLayout(self.widget2)
        self.Lanes.setSpacing(0)
        self.Lanes.setObjectName(u"Lanes")
        self.Lanes.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.Lanes.setContentsMargins(0, 0, 0, 0)
        self.widget3 = QWidget(self.widget2)
        self.widget3.setObjectName(u"widget3")
        sizePolicy.setHeightForWidth(self.widget3.sizePolicy().hasHeightForWidth())
        self.widget3.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QHBoxLayout(self.widget3)
        self.horizontalLayout_2.setSpacing(8)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(8, 0, 4, 4)
        self.label_3 = QLabel(self.widget3)
        self.label_3.setObjectName(u"label_3")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.label_3)


        self.Lanes.addWidget(self.widget3)

        self.widget_2 = QWidget(self.widget2)
        self.widget_2.setObjectName(u"widget_2")
        self.gridLayout_2 = QGridLayout(self.widget_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(0)
        self.gridLayout_2.setVerticalSpacing(18)
        self.gridLayout_2.setContentsMargins(16, 8, 16, 8)
        self.label_18 = QLabel(self.widget_2)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setMinimumSize(QSize(0, 13))
        self.label_18.setMaximumSize(QSize(16777215, 13))
        self.label_18.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_18, 9, 0, 1, 1)

        self.label_12 = QLabel(self.widget_2)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setMinimumSize(QSize(0, 13))
        self.label_12.setMaximumSize(QSize(16777215, 13))
        self.label_12.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_12, 3, 0, 1, 1)

        self.label_8 = QLabel(self.widget_2)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMinimumSize(QSize(0, 13))
        self.label_8.setMaximumSize(QSize(16777215, 13))
        self.label_8.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_8, 2, 1, 1, 1)

        self.label_22 = QLabel(self.widget_2)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setMinimumSize(QSize(0, 13))
        self.label_22.setMaximumSize(QSize(16777215, 13))
        self.label_22.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_22, 11, 1, 1, 1)

        self.label_20 = QLabel(self.widget_2)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setMinimumSize(QSize(0, 13))
        self.label_20.setMaximumSize(QSize(16777215, 13))
        self.label_20.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_20, 12, 1, 1, 1)

        self.label_9 = QLabel(self.widget_2)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMinimumSize(QSize(0, 13))
        self.label_9.setMaximumSize(QSize(16777215, 13))
        self.label_9.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_9, 4, 1, 1, 1)

        self.label_5 = QLabel(self.widget_2)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(0, 13))
        self.label_5.setMaximumSize(QSize(16777215, 13))
        self.label_5.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_5, 0, 1, 1, 1)

        self.label_25 = QLabel(self.widget_2)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setMinimumSize(QSize(0, 13))
        self.label_25.setMaximumSize(QSize(16777215, 13))
        self.label_25.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_25, 6, 0, 1, 1)

        self.label_11 = QLabel(self.widget_2)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setMinimumSize(QSize(0, 13))
        self.label_11.setMaximumSize(QSize(16777215, 13))
        self.label_11.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_11, 1, 0, 1, 1)

        self.label_26 = QLabel(self.widget_2)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setMinimumSize(QSize(0, 13))
        self.label_26.setMaximumSize(QSize(16777215, 13))
        self.label_26.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_26, 10, 1, 1, 1)

        self.label_21 = QLabel(self.widget_2)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setMinimumSize(QSize(0, 13))
        self.label_21.setMaximumSize(QSize(16777215, 13))
        self.label_21.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_21, 7, 0, 1, 1)

        self.label_16 = QLabel(self.widget_2)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setMinimumSize(QSize(0, 13))
        self.label_16.setMaximumSize(QSize(16777215, 13))
        self.label_16.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_16, 5, 0, 1, 1)

        self.label_31 = QLabel(self.widget_2)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setMinimumSize(QSize(0, 13))
        self.label_31.setMaximumSize(QSize(16777215, 13))
        self.label_31.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_31, 13, 0, 1, 1)

        self.label_15 = QLabel(self.widget_2)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setMinimumSize(QSize(0, 13))
        self.label_15.setMaximumSize(QSize(16777215, 13))
        self.label_15.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_15, 4, 0, 1, 1)

        self.label_28 = QLabel(self.widget_2)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setMinimumSize(QSize(0, 13))
        self.label_28.setMaximumSize(QSize(16777215, 13))
        self.label_28.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_28, 11, 0, 1, 1)

        self.label_29 = QLabel(self.widget_2)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setMinimumSize(QSize(0, 13))
        self.label_29.setMaximumSize(QSize(16777215, 13))
        self.label_29.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_29, 6, 1, 1, 1)

        self.label_27 = QLabel(self.widget_2)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setMinimumSize(QSize(0, 13))
        self.label_27.setMaximumSize(QSize(16777215, 13))
        self.label_27.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_27, 7, 1, 1, 1)

        self.label_23 = QLabel(self.widget_2)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setMinimumSize(QSize(0, 13))
        self.label_23.setMaximumSize(QSize(16777215, 13))
        self.label_23.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_23, 10, 0, 1, 1)

        self.label_17 = QLabel(self.widget_2)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setMinimumSize(QSize(0, 13))
        self.label_17.setMaximumSize(QSize(16777215, 13))
        self.label_17.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_17, 5, 1, 1, 1)

        self.label_7 = QLabel(self.widget_2)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(0, 13))
        self.label_7.setMaximumSize(QSize(16777215, 13))
        self.label_7.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_7, 3, 1, 1, 1)

        self.label_6 = QLabel(self.widget_2)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMinimumSize(QSize(0, 13))
        self.label_6.setMaximumSize(QSize(16777215, 13))
        self.label_6.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_6, 1, 1, 1, 1)

        self.label_13 = QLabel(self.widget_2)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setMinimumSize(QSize(0, 13))
        self.label_13.setMaximumSize(QSize(16777215, 13))
        self.label_13.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_13, 2, 0, 1, 1)

        self.label_10 = QLabel(self.widget_2)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMinimumSize(QSize(0, 13))
        self.label_10.setMaximumSize(QSize(16777215, 13))
        self.label_10.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_10, 0, 0, 1, 1)

        self.label_24 = QLabel(self.widget_2)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setMinimumSize(QSize(0, 13))
        self.label_24.setMaximumSize(QSize(16777215, 13))
        self.label_24.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_24, 9, 1, 1, 1)

        self.label_33 = QLabel(self.widget_2)
        self.label_33.setObjectName(u"label_33")
        self.label_33.setMinimumSize(QSize(0, 13))
        self.label_33.setMaximumSize(QSize(16777215, 13))
        self.label_33.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_33, 13, 1, 1, 1)

        self.label_19 = QLabel(self.widget_2)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setMinimumSize(QSize(0, 13))
        self.label_19.setMaximumSize(QSize(16777215, 13))
        self.label_19.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_19, 12, 0, 1, 1)

        self.label_30 = QLabel(self.widget_2)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setMinimumSize(QSize(0, 13))
        self.label_30.setMaximumSize(QSize(16777215, 13))

        self.gridLayout_2.addWidget(self.label_30, 8, 1, 1, 1)


        self.Lanes.addWidget(self.widget_2)


        self.verticalLayout.addWidget(self.widget2)

        self.Bottom = QHBoxLayout()
        self.Bottom.setObjectName(u"Bottom")
        self.Bottom.setContentsMargins(-1, 8, -1, -1)
        self.b_save = QPushButton(Edit_Query_Dialog)
        self.b_save.setObjectName(u"b_save")
        self.b_save.setMinimumSize(QSize(32, 32))
        self.b_save.setMaximumSize(QSize(16777215, 32))
        icon = QIcon()
        icon.addFile(u":/icons/icons/Done_dark.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.b_save.setIcon(icon)

        self.Bottom.addWidget(self.b_save)

        self.b_delete = QPushButton(Edit_Query_Dialog)
        self.b_delete.setObjectName(u"b_delete")
        self.b_delete.setMinimumSize(QSize(32, 32))
        self.b_delete.setMaximumSize(QSize(16777215, 32))
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons/Delete.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.b_delete.setIcon(icon1)

        self.Bottom.addWidget(self.b_delete)


        self.verticalLayout.addLayout(self.Bottom)


        self.retranslateUi(Edit_Query_Dialog)

        self.b_save.setDefault(True)


        QMetaObject.connectSlotsByName(Edit_Query_Dialog)
    # setupUi

    def retranslateUi(self, Edit_Query_Dialog):
        Edit_Query_Dialog.setWindowTitle(QCoreApplication.translate("Edit_Query_Dialog", u"Edit Query", None))
        self.label_2.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Preview", None))
        self.label_2.setProperty(u"class", QCoreApplication.translate("Edit_Query_Dialog", u"label", None))
        self.widget1.setProperty(u"class", QCoreApplication.translate("Edit_Query_Dialog", u"container", None))
        self.l_preview.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Preview Label", None))
        self.label_4.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Query", None))
        self.label_4.setProperty(u"class", QCoreApplication.translate("Edit_Query_Dialog", u"label", None))
        self.widget_6.setProperty(u"class", QCoreApplication.translate("Edit_Query_Dialog", u"container", None))
        self.label_14.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Ego Car", None))
        self.label_32.setText(QCoreApplication.translate("Edit_Query_Dialog", u"UMLSL", None))
        self.label_3.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Help", None))
        self.label_3.setProperty(u"class", QCoreApplication.translate("Edit_Query_Dialog", u"label", None))
        self.widget_2.setProperty(u"class", QCoreApplication.translate("Edit_Query_Dialog", u"container", None))
        self.label_18.setText(QCoreApplication.translate("Edit_Query_Dialog", u"\\neg \U0001d719", None))
        self.label_12.setText(QCoreApplication.translate("Edit_Query_Dialog", u"<\U0001d719>", None))
        self.label_8.setText(QCoreApplication.translate("Edit_Query_Dialog", u"No Car", None))
        self.label_22.setText(QCoreApplication.translate("Edit_Query_Dialog", u"\U0001d7191 \U00002228 \U0001d7192", None))
        self.label_20.setText(QCoreApplication.translate("Edit_Query_Dialog", u"\u2200 / For All Cars c", None))
        self.label_9.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Reserved Space", None))
        self.label_5.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Car c", None))
        self.label_25.setText(QCoreApplication.translate("Edit_Query_Dialog", u"\\hchop {\U0001d7191}{\U0001d7192}", None))
        self.label_11.setText(QCoreApplication.translate("Edit_Query_Dialog", u"cs", None))
        self.label_26.setText(QCoreApplication.translate("Edit_Query_Dialog", u"\U0001d7191 \U00002227 \U0001d7192", None))
        self.label_21.setText(QCoreApplication.translate("Edit_Query_Dialog", u"\\vchop {\U0001d7191} {\U0001d7192}", None))
        self.label_16.setText(QCoreApplication.translate("Edit_Query_Dialog", u"cl(c)", None))
        self.label_31.setText(QCoreApplication.translate("Edit_Query_Dialog", u"\\forall c \U0001d719", None))
        self.label_15.setText(QCoreApplication.translate("Edit_Query_Dialog", u"re(c)", None))
        self.label_28.setText(QCoreApplication.translate("Edit_Query_Dialog", u"\U0001d7191 \\or \U0001d7192", None))
        self.label_29.setText(QCoreApplication.translate("Edit_Query_Dialog", u"\U0001d7191 \U00002322 \U0001d7192", None))
        self.label_27.setText(QCoreApplication.translate("Edit_Query_Dialog", u"\U0001d7191", None))
        self.label_23.setText(QCoreApplication.translate("Edit_Query_Dialog", u"\U0001d7191 \\and \U0001d7192", None))
        self.label_17.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Clainmed Space", None))
        self.label_7.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Somewhere", None))
        self.label_6.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Crossing Segment", None))
        self.label_13.setText(QCoreApplication.translate("Edit_Query_Dialog", u"free", None))
        self.label_10.setText(QCoreApplication.translate("Edit_Query_Dialog", u"c", None))
        self.label_24.setText(QCoreApplication.translate("Edit_Query_Dialog", u"\U000000ac \U0001d719", None))
        self.label_33.setText(QCoreApplication.translate("Edit_Query_Dialog", u"\u2203 / Exists Car c", None))
        self.label_19.setText(QCoreApplication.translate("Edit_Query_Dialog", u"\\exists c \U0001d719", None))
        self.label_30.setText(QCoreApplication.translate("Edit_Query_Dialog", u"\U0001d7192", None))
        self.b_save.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Save", None))
        self.b_delete.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Delete", None))
    # retranslateUi

