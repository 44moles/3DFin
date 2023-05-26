import sys
from pathlib import Path
from typing import Optional

from pydantic import ValidationError
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QFileDialog, QMainWindow, QWidget

from three_d_fin.gui.expert_dlg import Ui_Dialog
from three_d_fin.gui.main_window import Ui_MainWindow
from three_d_fin.processing.abstract_processing import FinProcessing
from three_d_fin.processing.configuration import FinConfiguration


class ExpertDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

class Application(QMainWindow):
    params = FinConfiguration

    def __init__(
        self,
        processing_object: FinProcessing,
        file_externally_defined: bool = False,
        cloud_fields: Optional[set[str]] = None,
        parent: QWidget = None
    ):
        """Construct the 3DFin GUI Application.

        Parameters
        ----------
        processing_object : FinProcessing
            An implementation of the abstract FinProcessing class.
            it is responsible for the computing logic.
            Its process() method is triggered by the "compute" button of the GUI.
        file_externally_defined : bool
            Whether or not the file/filename was already defined by a third party.
            if True, input_las input and buttons will be disabled.
        cloud_fields : Optional[list[str]]
            List of candidates fields for the Z0 field. If present (not None),
            the z0_entry will be turned into a dropdown menu. If present but void,
            height normalization radio buttons will be disabled.
            TODO: we can imagine, no z0 fields and z == z0
        """
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.processing_object = processing_object
        self.file_externally_defined = file_externally_defined
        self.cloud_fields = cloud_fields

        # Force current index to be 0, since QT creator could change that
        self.ui.tabWidget.setCurrentIndex(0)
        self.setWindowIcon(QtGui.QIcon(":/assets/three_d_fin/assets/icon_window.ico"))

        # Click on the "documentation"
        self.ui.documentation_link_btn.clicked.connect(self.show_documentation)

        # Click on the "?" button on the expert table
        self.ui.expert_info_btn.clicked.connect(self.show_expert_dialog)

        # Click on input
        self.ui.input_file_btn.clicked.connect(self.input_file_clicked)

        # Click on output
        self.ui.output_dir_btn.clicked.connect(self.output_dir_clicked)

        # Click on compute
        self.ui.compute_btn.clicked.connect(self.compute_clicked)

        # Connect is_normalized
        self.ui.is_normalized_chk.toggled.connect(self.normalize_toggled)

        self._load_config_or_default()
        self._populate_fields()

    def _load_config_or_default(self):
        """Try to load a config file or fallback to default.

        TODO: Maybe it should be migrated into the FinProcessing constructor
        """
        try:
            # Reading config file only if it is available under name '3DFinconfig.ini'
            config_file_path = Path("3DFinconfig.ini")
            self.params = FinConfiguration.From_config_file(
                config_file_path.resolve(strict=True), init_misc=True
            )
            print("Configuration file found. Setting default parameters from the file")
        except ValidationError:
            print("Configuration file error")
            self.params = FinConfiguration()
        except FileNotFoundError:
            # No error message in this case, fallback to default parameters
            self.params = FinConfiguration()
        self.params = FinConfiguration()

    def _populate_fields(self):
        """Populate fields, label, tooltip based on FinConfiguration."""
        # params and QT fields have the same name, we take advantage of that
        config_dict = self.params.dict()
        for config_section in config_dict:
            for key_param, value_param in config_dict[config_section].items():
                # Default z0_name should match one of the supplied list if present.
                # TODO
                #if (key_param == "z0_name") and self.cloud_fields is not None:
                #    if value_param in self.cloud_fields:
                #        getattr(self.ui, key_param).set(value_param)
                # Fix a minor presentation issue when no file is defined
                if key_param == "input_file" and value_param is None:
                    self.ui.input_file_in.setText("")
                elif key_param == "is_normalized":
                   self.ui.is_normalized_chk.setChecked(not value_param) # TODO change = do_normalize
                elif key_param == "is_noisy":
                    self.ui.is_noisy_chk.setChecked(value_param)
                elif key_param == "export_txt":
                    self.ui.export_txt_rb_1.setChecked(value_param)
                    self.ui.export_txt_rb_2.setChecked(not value_param) 
                else:
                    getattr(self.ui, key_param + "_in").setText(str(value_param))
    
    def show_expert_dialog(self):
        """Show the expert help/warning dialog."""
        dialog = ExpertDialog(self)
        dialog.show()

    def show_documentation(self):
        """Show the documentation.

        Open the default PDF viewer to show the documentation.
        """
        try:
            base_path = Path(sys._MEIPASS)
        except Exception:
            base_path = Path(__file__).absolute().parents[1] / "documentation"
        QtGui.QDesktopServices.openUrl(
            QtCore.QUrl.fromLocalFile(str(Path(base_path / "documentation.pdf")))
        )

    def input_file_clicked(self):
        input_dialog = QFileDialog(self)
        if input_dialog.exec_():
            self.ui.input_file_in.setText(input_dialog.selectedFiles()[0])

    def output_dir_clicked(self):
        input_dialog = QFileDialog(self)
        if input_dialog.exec_():
            self.ui.output_dir_in.setText(input_dialog.selectedFiles()[0])

    def compute_clicked(self):
        placeholder = QDialog(self)
        placeholder.show()
    
    def normalize_toggled(self):
        self.ui.is_noisy_chk.setEnabled(self.ui.is_normalized_chk.isChecked())
        self.ui.z0_name_in.setEnabled(not self.ui.is_normalized_chk.isChecked())
        self.ui.z0_name_lbl.setEnabled(not self.ui.is_normalized_chk.isChecked())        
