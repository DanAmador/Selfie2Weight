import React, {Fragment} from 'react'
import ReactDOM from 'react-dom'
import './styles.css'
import CSVReader from 'react-csv-reader'
import Cropper from 'react-cropper';
import 'cropperjs/dist/cropper.css'; // see installation section above for versions of NPM older than 3.0.0

const cropper = React.createRef(null);

class App extends React.Component {
    state = {
        imageSrc: null,
        csvSrc: null,
        crop: {x: 0, y: 0},
        zoom: 1,
        aspect: 4 / 3,
        croppedAreaPixels: null,
        croppedImage: null,
        isCropping: false,
        cropResult: null,
    }

    constructor(props) {
        super(props);
        this.cropImage = this.cropImage.bind(this);
        this.onChange = this.onChange.bind(this);
    }

    onChange(e) {
        e.preventDefault();
        let files;
        if (e.dataTransfer) {
            files = e.dataTransfer.files;
        } else if (e.target) {
            files = e.target.files;
        }
        const reader = new FileReader();
        reader.onload = () => {
            this.setState({src: reader.result});
        };
        reader.readAsDataURL(files[0]);
    }

    onCsvLoaded = async (data, fileInfo) => {
        console.log(fileInfo)
        console.log(data)
        for (let entry in data) {
            let e = data[entry]
            if (e.sanitized === "False") {
                console.log(e.id)
                let imageDataUrl = "http://127.0.0.1:5000/img/" + e.id

                this.setState({
                    imageSrc: imageDataUrl,
                    crop: {x: 0, y: 0},
                    zoom: 1,
                })
                break
            }
        }

    }

    cropImage() {
        if (typeof this.cropper.getCroppedCanvas() === 'undefined') {
            return;
        }
        this.setState({
            cropResult: this.cropper.getCroppedCanvas().toDataURL(),
        });
    }

    render() {
        return (
            <div className="App">
                <CSVReader cssClass="csv-reader-input"

                           onFileLoaded={this.onCsvLoaded}
                           parserOptions={
                               {
                                   header: true,
                                   dynamicTyping: true,
                                   skipEmptyLines: true
                               }
                           }/>
                <div>
                    <div style={{width: '100%'}}>
                        <Cropper
                            style={{height: 400, width: '100%'}}
                            aspectRatio={16 / 9}
                            preview=".img-preview"
                            guides={false}
                            src={this.state.imageSrc}
                            ref={cropper => {
                                this.cropper = cropper;
                            }}
                        />
                    </div>
                    <div>
                        <div className="box" style={{width: '50%', float: 'right'}}>
                            <h1>Preview</h1>
                            <div className="img-preview" style={{width: '100%', float: 'left', height: 300}}/>
                        </div>
                        <div className="box" style={{width: '50%', float: 'right'}}>
                            <h1>
                                <span>Crop</span>
                                <button onClick={this.cropImage} style={{float: 'right'}}>
                                    Crop Image
                                </button>
                            </h1>
                            <img style={{width: '100%'}} src={this.state.cropResult} alt="cropped image"/>
                        </div>
                    </div>
                    <br style={{clear: 'both'}}/>
                </div>
            </div>


        )
    }
}

function readFile(file) {
    return new Promise(resolve => {
        const reader = new FileReader()
        reader.addEventListener('load', () => resolve(reader.result), false)
        reader.readAsDataURL(file)
    })
}

const rootElement = document.getElementById('root')
ReactDOM.render(<App/>, rootElement)
