import axios from "axios";
import { useRef, useState } from "react";
import "./App.css";
function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);
  const [imgPath, setImgPath] = useState("");
  const [showLoading, setShowLoading] = useState(false);
  const [showNotRecognize, setShowNotRecognize] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);

    // Preview the image
    const reader = new FileReader();
    reader.onload = () => {
      setPreviewImage(reader.result);
      setImgPath("");

      setShowNotRecognize(false);
    };
    reader.readAsDataURL(file);

    // Reset the file input value
    fileInputRef.current.value = null;
  };

  const handleUpload = () => {
    setShowLoading(true);
    if (selectedFile) {
      const formData = new FormData();
      formData.append("file", selectedFile);

      axios
        .post("/api/image", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        })
        .then((response) => {
          if (response.data?.detect) {
            setImgPath(response.data?.image);
            setShowLoading(false);
            showNotRecognize(false);
          } else {
            showNotRecognize(true);
          }
        })
        .catch((error) => {
          console.error(error);
          setShowLoading(false);
        });

      // Reset the selected file after upload
      setSelectedFile(null);
      return;
    }
    setShowLoading(false);
    alert("Not file selected!");
  };

  return (
    <div className="App">
      <div className="face-detection">
        <h1>Face Detection</h1>
        <div className="face-container">
          <div>
            {previewImage ? (
              <img
                src={
                  imgPath
                    ? `http://127.0.0.1:5000/image/${imgPath}`
                    : previewImage
                }
                alt="Preview"
                className="preview-face"
              />
            ) : (
              <div className="placeholder">
                <p>
                  No picture selected. Please select one picture to recognize!
                </p>
              </div>
            )}
          </div>
          <div style={{ display: "flex", "margin-top": "30px" }}>
            <div className="button-group">
              <input
                type="file"
                ref={fileInputRef}
                hidden
                onChange={handleFileChange}
              />
              <button
                className="choose-file-btn"
                onClick={() => {
                  fileInputRef.current.click();
                }}
              >
                Choose file
              </button>
              <button onClick={handleUpload}>Detect</button>
            </div>
            {showLoading && (
              <div className="lds-ring">
                <div></div>
                <div></div>
                <div></div>
                <div></div>
              </div>
            )}
            {showNotRecognize && (
              <div className="placeholder">
                <p>
                  <strong>Can not recognize any face in picture!</strong>
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
