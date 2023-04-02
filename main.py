import sys
import os
import requests
from time import sleep
from PyQt6 import QtWidgets, QtGui, QtCore
from pytube import YouTube

# le onde esta o arquivo e captura o nome do path
basedir = os.path.dirname(__file__)


# cria a classe worker
class WorkerDownloader(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(float)
    msg = QtCore.pyqtSignal(str)

    def __init__(self, video_object, path_download, resolution):
        super().__init__()

        self.video_object = video_object
        self.path_download = path_download
        self.resolution = resolution

    def run(self):
        # ========= baixar o video ===========
        try:
            YouTube.register_on_progress_callback(self.video_object,
                                                  self.emissor)
            down_video = self.video_object.streams.get_by_resolution(
                self.resolution)
            down_video.download(output_path=self.path_download)
        except Exception as error:
            self.msg.emit(f'erro no download: {error}')
        finally:
            self.finished.emit()

    def emissor(self, stream, chunk, bytes_remaining):
        # max_width = 100
        filesize = stream.filesize
        bytes_received = filesize - bytes_remaining
        """filled = int(round(max_width * bytes_received / float(filesize)))
        remaining = max_width - filled"""
        percent = round(100.0 * bytes_received / float(filesize), 1)
        self.progress.emit(percent)


# cria a classe progress bar
class progressBar(QtWidgets.QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMaximum(100)
        self._active = False

    def update_bar(self, i):
        if i <= 100:
            sleep(0.01)
            value = int(i)
            self.setValue(value)


# cria aplicativo principal
class YoutubeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.diretorio_downloads = './DOWNLOADS'
        self.link = ''
        self.video_object = object
        self.resolutions_availables = list()

        if not os.path.isdir(self.diretorio_downloads):
            os.mkdir(self.diretorio_downloads)

        self.setUI()

    def setUI(self):
        # ****************** CRIA JANELA PRINCIPAL ********************
        self.setWindowTitle('Youtube App Downloader')
        self.setFixedSize(500, 600)
        # --- obtem o tamanho da tela e centraliza o app ---
        screen_size = QtGui.QGuiApplication.primaryScreen().availableGeometry()
        x = (screen_size.width() - self.size().width()) // 2
        y = (screen_size.height() - self.size().height()) // 2
        self.move(x, y)

        #                +++ criar layout principal +++
        self.main_layout = QtWidgets.QVBoxLayout()
        self.stack_layout = QtWidgets.QStackedLayout()
        # ****************** FIM JANELA PRINCIPAL **********************

        # ***************** CRIA PAGINA DE DOWNLOAD ********************
        self.page_download = QtWidgets.QWidget()
        self.page_download_layout = QtWidgets.QVBoxLayout()
        #                     +++ labels e itens +++
        self.label_page_download = QtWidgets.QLabel()
        self.label_page_download.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.label_page_download.setText('Download videos')
        self.label_page_download.setFont(QtGui.QFont('Arial', 14))
        #                    +++ botão colar url +++
        self.page_download_paste_btn = QtWidgets.QPushButton()
        self.page_download_paste_btn.setText(
            'Carregar Vídeo')
        self.page_download_paste_btn.clicked.connect(
            self.capturar_area_de_transferencia)
        #                    +++ titulo do video +++
        self.label_page_download_titulo_video = QtWidgets.QLabel()
        enunciado_titulo = 'Siga as instruções abaixo.'
        self.label_page_download_titulo_video.setText(enunciado_titulo)
        self.label_page_download_titulo_video.setFixedSize(480, 50)
        self.label_page_download_titulo_video.setWordWrap(True)
        self.label_page_download_titulo_video.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_page_download_titulo_video.setFont(QtGui.QFont('Arial', 11))
        #                    +++ miniatura do video +++
        self.label_download_imagem_preview_label = QtWidgets.QLabel()
        self.label_download_imagem_preview_label.setFixedSize(480, 270)
        self.label_download_imagem_preview_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter)
        #         +++ label para seleção de resolução de video +++
        self.label_page_download_select_resolution = QtWidgets.QLabel()
        self.label_page_download_select_resolution.setText(
            'Selecione a resolução que deseja baixar o vídeo.')
        self.label_page_download_select_resolution.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignHCenter)
        #         +++ seleção de resoluções de video disponiveis +++
        self.page_download_select_resolution = QtWidgets.QComboBox()
        self.page_download_select_resolution.setPlaceholderText('Carregue o vídeo primeiro')
        #                 +++ label para a progress_bar +++
        self.label_download_progress_bar = QtWidgets.QLabel()
        self.label_download_progress_bar.setText('Progresso do download: ')
        #                       +++ progress_bar ++++
        self.download_progress_bar = progressBar()
        self.download_progress_bar.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignHCenter)
        #                 +++ botão para baixar o video +++
        self.page_download_button_for_download = QtWidgets.QPushButton()
        self.page_download_button_for_download.setText('Iniciar Download')
        self.page_download_button_for_download.clicked.connect(
            self.video_download_task)
        self.page_download_button_for_download.setEnabled(False)
        #           ------ adiciona as labels e itens -------
        self.page_download_layout.addWidget(self.label_page_download)
        self.page_download_layout.addWidget(self.page_download_paste_btn)
        self.page_download_layout.addWidget(
            self.label_page_download_titulo_video)
        self.page_download_layout.addWidget(
            self.label_download_imagem_preview_label)
        self.page_download_layout.addWidget(
            self.label_page_download_select_resolution)
        self.page_download_layout.addWidget(
            self.page_download_select_resolution)
        self.page_download_layout.addWidget(self.label_download_progress_bar)
        self.page_download_layout.addWidget(self.download_progress_bar)
        self.page_download_layout.addWidget(
            self.page_download_button_for_download)
        #        ----- pagina layout/add no stacklayout -----
        self.page_download.setLayout(self.page_download_layout)
        self.stack_layout.addWidget(self.page_download)

        # =========== criar ações dos botões do menu ============
        #                       Botão menu 1
        btn_menu_act_1 = QtGui.QAction(QtGui.QIcon(
            './images/download.ico'), 'Download videos', self)
        btn_menu_act_1.setStatusTip('Baixar videos através da URL.')
        btn_menu_act_1.triggered.connect(self.btn_menu_1)
        #                       Botão menu 2
        btn_menu_act_2 = QtGui.QAction(QtGui.QIcon(
            './images/instrucoes.ico'), 'Instruções de utilização', self)
        btn_menu_act_2.setStatusTip('Exibe as intruções de utilização do aplicativo.')
        btn_menu_act_2.triggered.connect(self.btn_menu_2)

        # ============= exibir as dicas na barra de status =======
        self.setStatusBar(QtWidgets.QStatusBar(self))

        # ================= invoca a barra de menu =================
        menu = self.menuBar()
        #           ------- adiciona os itens ao menuBar ------
        main_menu = menu.addMenu('Menu')
        main_menu.addAction(btn_menu_act_1)
        main_menu.addSeparator()
        main_menu.addAction(btn_menu_act_2)

        # ============== define o widget principal =================
        widget = QtWidgets.QWidget()
        self.main_layout.addLayout(self.stack_layout)
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        self.exibir_instrucoes()

    # ******************** CRIAÇÃO DOS BOTÕES DO MENU *****************
    def btn_menu_1(self):
        self.stack_layout.setCurrentIndex(0)

    def btn_menu_2(self):
        self.exibir_instrucoes()
    # ************************* FIM BOTÕES MENU ************************

    # ****************** FUNÇÕES DE IMPLEMENTAÇÃO *********************
    def capturar_area_de_transferencia(self):
        text = QtWidgets.QApplication.clipboard().text()
        if text.startswith('https://www.yout') or text.startswith('http://www.yout'):
            self.link = text
            self.video_object = YouTube(self.link)
            self.titulo_e_miniatura()
            self.get_resolutions_list()
            self.page_download_button_for_download.setEnabled(True)
            self.download_progress_bar.update_bar(0)
        else:
            text = ''
            self.label_page_download_titulo_video.setText(
                'Este não é um URL válido. Por favor copie um endereço do Youtube')

    def titulo_e_miniatura(self):
        self.label_page_download_titulo_video.setText(self.video_object.title)
        url_image = self.video_object.thumbnail_url
        image = QtGui.QImage()
        image.loadFromData(requests.get(url_image).content)
        self.label_download_imagem_preview_label.setPixmap(
            QtGui.QPixmap(image).scaled(480, 355))

    def exibir_instrucoes(self):
        image = os.path.join(basedir, './images/tutorial.jpg')
        tutorial_image = QtGui.QImage(image)
        self.label_download_imagem_preview_label.setPixmap(
            QtGui.QPixmap(tutorial_image).scaled(480, 275))
        self.page_download_button_for_download.setEnabled(False)
        for item in range(len(self.resolutions_availables)+1):
            self.page_download_select_resolution.removeItem(0)
        self.label_page_download_titulo_video.setText('Siga as instruções abaixo.')

    def get_resolutions_list(self):
        for item in range(len(self.resolutions_availables)+1):
            self.page_download_select_resolution.removeItem(0)
        resolutions_avaiables = self.video_object.streams.filter(progressive=True)
        resolutions_avaiables = resolutions_avaiables.filter(fps=30)
        self.resolutions_availables = [
            item.resolution for item in resolutions_avaiables]
        self.page_download_select_resolution.addItems(
            self.resolutions_availables)
        self.page_download_select_resolution.setCurrentIndex(
            self.resolutions_availables.index(self.resolutions_availables[-1]))

    def video_download_task(self):
        btn_download = self.page_download_button_for_download
        btn_paste = self.page_download_paste_btn
        btn_select_res = self.page_download_select_resolution
        # ============ cria a thread e o worker =============
        self.thread = QtCore.QThread()
        self.worker = WorkerDownloader(self.video_object,
                                       self.diretorio_downloads,
                                       self.page_download_select_resolution.currentText())
        self.worker.moveToThread(self.thread)
        # ================ conecta sinais e slots ===========
        self.thread.started.connect(lambda: btn_download.setText('Download iniciado.'))
        self.thread.started.connect(self.worker.run)
        self.worker.msg.connect(self.report_msg)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.report_progress)
        #      ============ iniciar thread ===========
        self.thread.start()
        #       ========== desabilita os itens da interface ===========
        # ====== evita do usuário clicar onde não deve durante a terefa ===
        btn_download.setEnabled(False)
        btn_paste.setEnabled(False)
        btn_select_res.setEnabled(False)
        #       ======== ao terminar a thread reabilita a interface =========
        self.thread.finished.connect(lambda: btn_download.setEnabled(True))
        self.thread.finished.connect(lambda: btn_paste.setEnabled(True))
        self.thread.finished.connect(lambda: btn_select_res.setEnabled(True))
        self.thread.finished.connect(lambda: btn_download.setText('Iniciar Download'))
        self.thread.finished.connect(self.download_sucessful)
        self.thread.finished.connect(self.exibir_instrucoes)

    def report_progress(self, n):
        self.download_progress_bar.update_bar(n)

    def report_msg(self, s):
        self.label_page_download_titulo_video.setText(
            'Ocorreu um erro na aquisição do video, reinicie o aplicativo.')

    def download_sucessful(self):
        sleep(1)
        os.chdir(f'{self.diretorio_downloads}')
        os.startfile(r'')
        os.chdir('..')
    # ***************** FIM FUNÇÕES DE IMPLEMENTAÇÃO *******************


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, './images/main_icon.ico')))
    run = YoutubeApp()
    run.show()
    sys.exit(app.exec())
