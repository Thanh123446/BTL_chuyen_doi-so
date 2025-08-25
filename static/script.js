document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const recordBtn = document.getElementById('record-btn');
    const stopBtn = document.getElementById('stop-btn');
    const status = document.getElementById('status');
    const result = document.getElementById('result');

    let mediaRecorder;
    let audioChunks = [];

    // Kiểm tra hỗ trợ getUserMedia
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Trình duyệt của bạn không hỗ trợ ghi âm.');
        recordBtn.disabled = true;
        return;
    }

    // Xử lý tải lên file
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!fileInput.files.length) {
            result.value = 'Vui lòng chọn một tệp âm thanh.';
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        result.value = 'Đang xử lý...';
        try {
            console.log('Uploading file:', fileInput.files[0].name);
            const response = await fetch('/transcribe', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            console.log('Transcription result:', data);
            result.value = data.text;
        } catch (err) {
            console.error('Upload error:', err);
            result.value = 'Lỗi: ' + err.message;
        }
    });

    // Xử lý ghi âm
    recordBtn.addEventListener('click', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
            audioChunks = [];

            mediaRecorder.addEventListener('dataavailable', (event) => {
                audioChunks.push(event.data);
                console.log('Audio chunk received:', event.data);
            });

            mediaRecorder.addEventListener('stop', async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                console.log('Audio blob size:', audioBlob.size);
                const formData = new FormData();
                formData.append('audio', audioBlob, 'recording.webm');

                result.value = 'Đang xử lý...';
                try {
                    const response = await fetch('/transcribe', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    console.log('Transcription result:', data);
                    result.value = data.text;
                } catch (err) {
                    console.error('Transcription error:', err);
                    result.value = 'Lỗi: ' + err.message;
                }

                status.textContent = 'Trạng thái: Sẵn sàng';
                stream.getTracks().forEach(track => track.stop()); // Dừng micro
            });

            mediaRecorder.start();
            recordBtn.disabled = true;
            stopBtn.disabled = false;
            status.textContent = 'Trạng thái: Đang ghi âm...';
        } catch (err) {
            console.error('Micro error:', err);
            status.textContent = 'Lỗi: Không thể truy cập micro.';
        }
    });

    stopBtn.addEventListener('click', () => {
        if (mediaRecorder) {
            mediaRecorder.stop();
            recordBtn.disabled = false;
            stopBtn.disabled = true;
            status.textContent = 'Trạng thái: Đang dừng...';
        }
    });
});