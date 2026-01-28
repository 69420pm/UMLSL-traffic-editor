# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'car_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QComboBox, QDialog,
    QDoubleSpinBox, QGridLayout, QHBoxLayout, QLabel,
    QLayout, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_Edit_Car_Dialog(object):
    def setupUi(self, Edit_Car_Dialog):
        if not Edit_Car_Dialog.objectName():
            Edit_Car_Dialog.setObjectName(u"Edit_Car_Dialog")
        Edit_Car_Dialog.setEnabled(True)
        Edit_Car_Dialog.resize(320, 524)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Edit_Car_Dialog.sizePolicy().hasHeightForWidth())
        Edit_Car_Dialog.setSizePolicy(sizePolicy)
        Edit_Car_Dialog.setMinimumSize(QSize(320, 0))
        Edit_Car_Dialog.setMaximumSize(QSize(320, 999999))
        Edit_Car_Dialog.setStyleSheet(u"QDialog {\n"
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
"QLineEdit{\n"
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
"    border: 1px solid #042"
                        "F40; /* Your custom border */\n"
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
"    subcontrol-position: top right"
                        ";\n"
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
"    image: url(:/icons/icons/up.svg); /* You ne"
                        "ed to create this file */\n"
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
"    background-color: #314250; \n"
""
                        "}\n"
"QPushButton#b_delete:pressed {\n"
"    background-color: #042F40; \n"
"}")
        self.verticalLayout = QVBoxLayout(Edit_Car_Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget = QWidget(Edit_Car_Dialog)
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
        self.widget1.setMinimumSize(QSize(75, 0))
        self.gridLayout = QGridLayout(self.widget1)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.gridLayout.setHorizontalSpacing(4)
        self.gridLayout.setVerticalSpacing(8)
        self.gridLayout.setContentsMargins(8, 4, 4, 4)
        self.label_15 = QLabel(self.widget1)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setMinimumSize(QSize(75, 0))

        self.gridLayout.addWidget(self.label_15, 1, 0, 1, 1)

        self.lineEdit = QLineEdit(self.widget1)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumSize(QSize(0, 24))
        self.lineEdit.setMaximumSize(QSize(16777215, 24))

        self.gridLayout.addWidget(self.lineEdit, 1, 2, 1, 1)

        self.l_axis = QLabel(self.widget1)
        self.l_axis.setObjectName(u"l_axis")
        self.l_axis.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.l_axis, 2, 1, 1, 1)

        self.spinBox = QSpinBox(self.widget1)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setMinimumSize(QSize(0, 24))
        self.spinBox.setMaximumSize(QSize(16777215, 24))

        self.gridLayout.addWidget(self.spinBox, 2, 2, 1, 1)

        self.label_7 = QLabel(self.widget1)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(75, 0))

        self.gridLayout.addWidget(self.label_7, 4, 0, 1, 1)

        self.label_16 = QLabel(self.widget1)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_16, 1, 1, 1, 1)

        self.label_8 = QLabel(self.widget1)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_8, 0, 1, 1, 1)

        self.t_name = QLineEdit(self.widget1)
        self.t_name.setObjectName(u"t_name")
        self.t_name.setMinimumSize(QSize(0, 24))
        self.t_name.setMaximumSize(QSize(16777215, 24))
        self.t_name.setCursorPosition(0)

        self.gridLayout.addWidget(self.t_name, 0, 2, 1, 1)

        self.label_6 = QLabel(self.widget1)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMinimumSize(QSize(75, 0))

        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)

        self.s_position = QDoubleSpinBox(self.widget1)
        self.s_position.setObjectName(u"s_position")
        self.s_position.setMinimumSize(QSize(0, 24))
        self.s_position.setMaximumSize(QSize(16777215, 24))
        self.s_position.setMinimum(-100.000000000000000)
        self.s_position.setMaximum(100.000000000000000)
        self.s_position.setStepType(QAbstractSpinBox.StepType.DefaultStepType)

        self.gridLayout.addWidget(self.s_position, 4, 2, 1, 1)

        self.label_5 = QLabel(self.widget1)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(75, 0))
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_5, 0, 0, 1, 1)

        self.label_18 = QLabel(self.widget1)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setMinimumSize(QSize(75, 0))

        self.gridLayout.addWidget(self.label_18, 5, 0, 1, 1)

        self.doubleSpinBox = QDoubleSpinBox(self.widget1)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        self.doubleSpinBox.setMinimumSize(QSize(0, 24))
        self.doubleSpinBox.setMaximumSize(QSize(16777215, 24))
        self.doubleSpinBox.setMinimum(-100.000000000000000)
        self.doubleSpinBox.setMaximum(100.000000000000000)

        self.gridLayout.addWidget(self.doubleSpinBox, 5, 2, 1, 1)

        self.label = QLabel(self.widget1)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label, 4, 1, 1, 1)

        self.label_20 = QLabel(self.widget1)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_20, 5, 1, 1, 1)

        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 4)

        self.General.addWidget(self.widget1)


        self.verticalLayout.addWidget(self.widget)

        self.widget_4 = QWidget(Edit_Car_Dialog)
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
        self.gridLayout_3 = QGridLayout(self.widget_6)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setHorizontalSpacing(4)
        self.gridLayout_3.setVerticalSpacing(8)
        self.gridLayout_3.setContentsMargins(8, 4, 4, 4)
        self.label_9 = QLabel(self.widget_6)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMinimumSize(QSize(75, 0))

        self.gridLayout_3.addWidget(self.label_9, 3, 0, 1, 1)

        self.label_13 = QLabel(self.widget_6)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setMinimumSize(QSize(75, 0))

        self.gridLayout_3.addWidget(self.label_13, 1, 0, 1, 1)

        self.label_14 = QLabel(self.widget_6)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setMinimumSize(QSize(75, 0))
        self.label_14.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_3.addWidget(self.label_14, 0, 0, 1, 1)

        self.l_axis_2 = QLabel(self.widget_6)
        self.l_axis_2.setObjectName(u"l_axis_2")
        self.l_axis_2.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_3.addWidget(self.l_axis_2, 3, 1, 1, 1)

        self.s_position_2 = QDoubleSpinBox(self.widget_6)
        self.s_position_2.setObjectName(u"s_position_2")
        self.s_position_2.setMinimumSize(QSize(0, 24))
        self.s_position_2.setMaximumSize(QSize(16777215, 24))
        self.s_position_2.setMinimum(-500.000000000000000)
        self.s_position_2.setMaximum(500.000000000000000)
        self.s_position_2.setStepType(QAbstractSpinBox.StepType.DefaultStepType)

        self.gridLayout_3.addWidget(self.s_position_2, 3, 2, 1, 1)

        self.label_17 = QLabel(self.widget_6)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setMinimumSize(QSize(75, 0))

        self.gridLayout_3.addWidget(self.label_17, 4, 0, 1, 1)

        self.d_orientation_2 = QComboBox(self.widget_6)
        self.d_orientation_2.setObjectName(u"d_orientation_2")
        self.d_orientation_2.setMinimumSize(QSize(0, 24))
        self.d_orientation_2.setMaximumSize(QSize(16777215, 24))
        self.d_orientation_2.setFrame(False)

        self.gridLayout_3.addWidget(self.d_orientation_2, 0, 2, 1, 1)

        self.comboBox = QComboBox(self.widget_6)
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setMinimumSize(QSize(0, 24))
        self.comboBox.setMaximumSize(QSize(16777215, 24))

        self.gridLayout_3.addWidget(self.comboBox, 1, 2, 1, 1)

        self.doubleSpinBox_2 = QDoubleSpinBox(self.widget_6)
        self.doubleSpinBox_2.setObjectName(u"doubleSpinBox_2")
        self.doubleSpinBox_2.setMinimumSize(QSize(0, 24))
        self.doubleSpinBox_2.setMaximumSize(QSize(16777215, 24))
        self.doubleSpinBox_2.setMinimum(-0.990000000000000)
        self.doubleSpinBox_2.setMaximum(0.990000000000000)
        self.doubleSpinBox_2.setSingleStep(0.100000000000000)

        self.gridLayout_3.addWidget(self.doubleSpinBox_2, 4, 2, 1, 1)

        self.label_12 = QLabel(self.widget_6)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_3.addWidget(self.label_12, 4, 1, 1, 1)

        self.gridLayout_3.setColumnStretch(0, 1)
        self.gridLayout_3.setColumnStretch(1, 1)
        self.gridLayout_3.setColumnStretch(2, 4)

        self.General_2.addWidget(self.widget_6)


        self.verticalLayout.addWidget(self.widget_4)

        self.widget2 = QWidget(Edit_Car_Dialog)
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
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.label_3)


        self.Lanes.addWidget(self.widget3)

        self.widget_2 = QWidget(self.widget2)
        self.widget_2.setObjectName(u"widget_2")
        self.gridLayout_2 = QGridLayout(self.widget_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(4)
        self.gridLayout_2.setVerticalSpacing(8)
        self.gridLayout_2.setContentsMargins(8, 4, 4, 4)
        self.comboBox_2 = QComboBox(self.widget_2)
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.setObjectName(u"comboBox_2")
        self.comboBox_2.setMinimumSize(QSize(0, 24))
        self.comboBox_2.setMaximumSize(QSize(16777215, 24))
        self.comboBox_2.setMaxVisibleItems(3)

        self.gridLayout_2.addWidget(self.comboBox_2, 0, 2, 1, 1)

        self.comboBox_4 = QComboBox(self.widget_2)
        self.comboBox_4.setObjectName(u"comboBox_4")
        self.comboBox_4.setMinimumSize(QSize(0, 24))
        self.comboBox_4.setMaximumSize(QSize(16777215, 24))

        self.gridLayout_2.addWidget(self.comboBox_4, 3, 2, 1, 1)

        self.label_19 = QLabel(self.widget_2)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setMinimumSize(QSize(75, 0))

        self.gridLayout_2.addWidget(self.label_19, 3, 0, 1, 1)

        self.label_11 = QLabel(self.widget_2)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setMinimumSize(QSize(75, 0))

        self.gridLayout_2.addWidget(self.label_11, 2, 0, 1, 1)

        self.comboBox_3 = QComboBox(self.widget_2)
        self.comboBox_3.setObjectName(u"comboBox_3")
        self.comboBox_3.setMinimumSize(QSize(0, 24))
        self.comboBox_3.setMaximumSize(QSize(16777215, 24))

        self.gridLayout_2.addWidget(self.comboBox_3, 2, 2, 1, 1)

        self.label_10 = QLabel(self.widget_2)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMinimumSize(QSize(75, 0))

        self.gridLayout_2.addWidget(self.label_10, 0, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 0, 1, 1, 1)

        self.gridLayout_2.setColumnStretch(0, 1)
        self.gridLayout_2.setColumnStretch(1, 1)
        self.gridLayout_2.setColumnStretch(2, 4)

        self.Lanes.addWidget(self.widget_2)


        self.verticalLayout.addWidget(self.widget2)

        self.Bottom = QHBoxLayout()
        self.Bottom.setObjectName(u"Bottom")
        self.Bottom.setContentsMargins(-1, 8, -1, -1)
        self.b_save = QPushButton(Edit_Car_Dialog)
        self.b_save.setObjectName(u"b_save")
        self.b_save.setMinimumSize(QSize(32, 32))
        self.b_save.setMaximumSize(QSize(16777215, 32))
        icon = QIcon()
        icon.addFile(u":/icons/icons/Done_dark.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.b_save.setIcon(icon)

        self.Bottom.addWidget(self.b_save)

        self.b_delete = QPushButton(Edit_Car_Dialog)
        self.b_delete.setObjectName(u"b_delete")
        self.b_delete.setMinimumSize(QSize(32, 32))
        self.b_delete.setMaximumSize(QSize(16777215, 32))
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons/Delete.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.b_delete.setIcon(icon1)

        self.Bottom.addWidget(self.b_delete)


        self.verticalLayout.addLayout(self.Bottom)


        self.retranslateUi(Edit_Car_Dialog)
        self.b_delete.clicked.connect(Edit_Car_Dialog.reject)
        self.b_save.clicked.connect(Edit_Car_Dialog.accept)

        self.comboBox_2.setCurrentIndex(0)
        self.b_save.setDefault(True)


        QMetaObject.connectSlotsByName(Edit_Car_Dialog)
    # setupUi

    def retranslateUi(self, Edit_Car_Dialog):
        Edit_Car_Dialog.setWindowTitle(QCoreApplication.translate("Edit_Car_Dialog", u"Edit Car", None))
        self.label_2.setText(QCoreApplication.translate("Edit_Car_Dialog", u"General", None))
        self.label_2.setProperty(u"class", QCoreApplication.translate("Edit_Car_Dialog", u"label", None))
        self.widget1.setProperty(u"class", QCoreApplication.translate("Edit_Car_Dialog", u"container", None))
        self.label_15.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Color", None))
        self.l_axis.setText(QCoreApplication.translate("Edit_Car_Dialog", u"[1,5]", None))
        self.l_axis.setProperty(u"class", QCoreApplication.translate("Edit_Car_Dialog", u"hint", None))
        self.label_7.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Speed", None))
        self.label_16.setText(QCoreApplication.translate("Edit_Car_Dialog", u"hex", None))
        self.label_16.setProperty(u"class", QCoreApplication.translate("Edit_Car_Dialog", u"hint", None))
        self.label_8.setText(QCoreApplication.translate("Edit_Car_Dialog", u"unique", None))
        self.label_8.setProperty(u"class", QCoreApplication.translate("Edit_Car_Dialog", u"hint", None))
        self.t_name.setPlaceholderText("")
        self.label_6.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Length", None))
        self.label_5.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Name", None))
        self.label_18.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Acceleration", None))
        self.label.setText(QCoreApplication.translate("Edit_Car_Dialog", u"u/s", None))
        self.label.setProperty(u"class", QCoreApplication.translate("Edit_Car_Dialog", u"hint", None))
        self.label_20.setText(QCoreApplication.translate("Edit_Car_Dialog", u"u/s^2", None))
        self.label_20.setProperty(u"class", QCoreApplication.translate("Edit_Car_Dialog", u"hint", None))
        self.label_4.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Location", None))
        self.label_4.setProperty(u"class", QCoreApplication.translate("Edit_Car_Dialog", u"label", None))
        self.widget_6.setProperty(u"class", QCoreApplication.translate("Edit_Car_Dialog", u"container", None))
        self.label_9.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Position", None))
        self.label_13.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Lane", None))
        self.label_14.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Road", None))
        self.l_axis_2.setText(QCoreApplication.translate("Edit_Car_Dialog", u"x-Axis", None))
        self.l_axis_2.setProperty(u"class", QCoreApplication.translate("Edit_Car_Dialog", u"hint", None))
        self.label_17.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Transition", None))
        self.label_12.setText(QCoreApplication.translate("Edit_Car_Dialog", u"(-1,1)", None))
        self.label_12.setProperty(u"class", QCoreApplication.translate("Edit_Car_Dialog", u"hint", None))
        self.label_3.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Next Turn", None))
        self.label_3.setProperty(u"class", QCoreApplication.translate("Edit_Car_Dialog", u"label", None))
        self.widget_2.setProperty(u"class", QCoreApplication.translate("Edit_Car_Dialog", u"container", None))
        self.comboBox_2.setItemText(0, QCoreApplication.translate("Edit_Car_Dialog", u"left", None))
        self.comboBox_2.setItemText(1, QCoreApplication.translate("Edit_Car_Dialog", u"straight", None))
        self.comboBox_2.setItemText(2, QCoreApplication.translate("Edit_Car_Dialog", u"right", None))

        self.label_19.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Lane", None))
        self.label_11.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Road", None))
        self.label_10.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Direction", None))
        self.b_save.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Save", None))
        self.b_delete.setText(QCoreApplication.translate("Edit_Car_Dialog", u"Delete", None))
    # retranslateUi

