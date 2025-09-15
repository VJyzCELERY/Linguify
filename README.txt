Untuk penggunaan program requirement yang diperlukan adalah
Python 3.12

Jika memiliki GPU CUDA dan ingin menginstall aplikasi dengan penggunaan GPU maka pada file install_with_gpu_support.bat bisa diedit line
```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```
Untuk disesuainkan dengan versi pytorch yang sama dengan versi CUDA GPU anda.
Pada contoh ini yang diinstall adalah pytorch untuk GPU dengan CUDA 12.4
pastikan pytorch juga sesuai dengan operating system anda
untuk info selengkapnya bisa mengunjungi link https://pytorch.org/
Setelah mengubah file tersebut jalankan InstallWithGPU.bat

Jika tidak menggunakan GPU CUDA maka silahkan install melalui InstallWithoutGPU.bat

untuk penjalanan simulasi aplikasinya sendiri tinggal menggunakan salah satu dari start_server.bat

Contohnya jika menjalankan simulasi aplikasi (tampilan untuk smartphone) dengan GPU jalankan start_serverAppSimulatorGPU.bat
Jika tidak menggunakanGPU start_serverAppSimulatorNoGPU.bat

Jika ingin menjalankan webapp gunakan start_webserverGPU.bat atau start_webserverNoGPU.bat

Pada versi ini websocket mungkin kurang stabil, sehingga dapat terjadi bug dimana js client berhenti menerima format JSON dengan tepat, untuk sementara penanganan kejadian tersebut dapat dengan dilakukan refresh pada web app.

Penggunaan aplikasi hanya di tes kompatibilitas dengan windows dan sangat disarankan untuk menjalankan aplikasi melalui bat file yang sudah disediakan. Menjalankan python scriptnya langsung memungkinkan namun dapat menghasilkan instabilitas seperti terbuatnya file directory atau penunjukkan file directory yang tidak sesuai. Sehingga sangat dianjurkan menggunakan bat file yang disediakan.