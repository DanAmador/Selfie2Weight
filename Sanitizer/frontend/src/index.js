import React from 'react'
import ReactDOM from 'react-dom'
import './styles.css'
import Cropper from 'react-cropper';
import 'cropperjs/dist/cropper.css'; // see installation section above for versions of NPM older than 3.0.0

const cropper = React.createRef(null);
const BASE_URL = "http://127.0.0.1:5000"

class App extends React.Component {
    state = {
        imageSrc: null,
        crop: {x: 0, y: 0},
        zoom: 1,
        croppedAreaPixels: null,
        croppedImage: null,
        isCropping: false,
        cropResult: null,
        currCrop: 0,
        cropData: {},
        imgMeta: null,
    }

    constructor(props) {
        super(props);
        this.cropImage = this.cropImage.bind(this);
        this.onChange = this.onChange.bind(this);
        this.onNext = this.onNext.bind(this);
        this.onNext()
    }

    onNext(e) {
        fetch(`${BASE_URL}/next`).then(
            res => {
                return res.json();
            }
        ).then(data => {
            console.log(data)
            this.setState({
                imgMeta: data,
                imageSrc: `${BASE_URL}/img/${data["id"]}`,
                crop: {x: 0, y: 0},
                zoom: 1,
            })

        })
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


    cropImage() {
        if (typeof this.cropper.getCroppedCanvas() === 'undefined') {
            return;
        }

        let crops = this.state.cropData;
        console.log(crops)
        crops[this.state.currCrop] = this.cropper.getData()
        this.setState({
            cropResult: this.cropper.getCroppedCanvas().toDataURL(),
            cropData: crops
        });
    }

    render() {
        return (
            <div className="App">

                <div>
                    <div style={{width: '100%'}}>
                        <Cropper
                            style={{height: 400, width: '100%'}}
                            preview=".img-preview"
                            guides={false}
                            src={this.state.imageSrc}
                            ref={cropper => {
                                this.cropper = cropper;
                            }}
                            guides={false}

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

const rootElement = document.getElementById('root')
ReactDOM.render(<App/>, rootElement)
