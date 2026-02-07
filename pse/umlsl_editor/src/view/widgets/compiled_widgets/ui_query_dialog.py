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
    QPushButton, QSizePolicy, QTextEdit, QToolButton,
    QVBoxLayout, QWidget)
from . import resources_rc

class Ui_Edit_Query_Dialog(object):
    def setupUi(self, Edit_Query_Dialog):
        if not Edit_Query_Dialog.objectName():
            Edit_Query_Dialog.setObjectName(u"Edit_Query_Dialog")
        Edit_Query_Dialog.setEnabled(True)
        Edit_Query_Dialog.resize(360, 477)
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
"}\n"
"\n"
"QToolButton {\n"
"    background-color: #032F40; \n"
"    border-radius: 16px;       \n"
"    border: none;\n"
"    text-align: center;\n"
"}\n"
"\n"
"QToolButton#b_sidebar_toggle {\n"
"    border-top-left-radius: 0px;\n"
"    border-top-right-radius: 16px;\n"
"    border-bottom-left-radius: 0px;\n"
"    border-bottom-right-radius: 16px;   \n"
"}\n"
"\n"
"QToolButton:hover {\n"
"    background-color: #084D68; \n"
"}\n"
"\n"
"QToolButton:pressed {\n"
"    background-color: #032F40;\n"
"}")
        self.verticalLayout = QVBoxLayout(Edit_Query_Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
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
        self.widget1.setMinimumSize(QSize(0, 0))
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
        self.l_preview.setMinimumSize(QSize(300, 100))
        self.l_preview.setMaximumSize(QSize(16777215, 16777215))
        self.l_preview.setScaledContents(False)
        self.l_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.l_preview.setWordWrap(True)

        self.gridLayout.addWidget(self.l_preview, 0, 0, 1, 1)


        self.General.addWidget(self.widget1)


        self.verticalLayout.addWidget(self.widget)

        self.widget_4 = QWidget(Edit_Query_Dialog)
        self.widget_4.setObjectName(u"widget_4")
        self.verticalLayout_2 = QVBoxLayout(self.widget_4)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(8, -1, -1, -1)
        self.label_4 = QLabel(self.widget_4)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft)
        self.label_4.setMargin(0)

        self.horizontalLayout_2.addWidget(self.label_4)

        self.b_help = QToolButton(self.widget_4)
        self.b_help.setObjectName(u"b_help")
        self.b_help.setMinimumSize(QSize(0, 32))
        self.b_help.setMaximumSize(QSize(16777215, 32))

        self.horizontalLayout_2.addWidget(self.b_help)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

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
        self.t_umlsl.setMinimumSize(QSize(0, 0))
        self.t_umlsl.setMaximumSize(QSize(16777215, 16777215))

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.t_umlsl)


        self.verticalLayout_2.addWidget(self.widget_6)


        self.verticalLayout.addWidget(self.widget_4)

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
        self.b_help.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Help", None))
        self.widget_6.setProperty(u"class", QCoreApplication.translate("Edit_Query_Dialog", u"container", None))
        self.label_14.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Ego Car", None))
        self.label_32.setText(QCoreApplication.translate("Edit_Query_Dialog", u"UMLSL", None))
        self.b_save.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Save", None))
        self.b_delete.setText(QCoreApplication.translate("Edit_Query_Dialog", u"Delete", None))
    # retranslateUi

