from ftplib import FTP, ftpcp


class FTP_Client():
    # todo: download path
    # todo: remote path

    HOSTNAME = "185.8.172.124"
    USERNAME = 'fweavertp'
    PASS = 'f12t34p56'

    ftp: FTP = None

    # todo: def init
    def __init__(self) -> None:
        try:
            self.ftp = FTP(host=self.HOSTNAME, user=self.USERNAME, passwd=self.PASS)
        except Exception as ex:
            print("error in ftp connection")
        pass

    def download(self, filename: str):
        if self.ftp is None:
            print("no ftp client")
            return

        with open(filename, "wb") as download_file:
            self.ftp.retrbinary(f"RETR {filename}", download_file.write)
        pass

    def close(self):
        if self.ftp is None:
            print("no ftp client")
            return

        self.ftp.close()


if __name__ == '__main__':
    ftp_server = FTP_Client()
    ftp_server.download("0.jpg")
    ftp_server.close()
