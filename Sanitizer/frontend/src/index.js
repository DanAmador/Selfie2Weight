import React from 'react'
import ReactDOM from 'react-dom'
import './styles.css'
import Cropper from 'react-cropper';

import 'cropperjs/dist/cropper.css'; // see installation section above for versions of NPM older than 3.0.0
import CropGallery from "./cropGallery"
import {Grid} from 'semantic-ui-react'

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
        currCrop: 0,
        cropData: [],
        cropMeta: [],
        imgMeta: null,
    }

    constructor(props) {
        super(props);
        this.cropImage = this.cropImage.bind(this);
        this.onChange = this.onChange.bind(this);
        this.onNext = this.onNext.bind(this);
        this.onIndexChange = this.onIndexChange.bind(this);

        this.onNext()
    }

    onNext(e) {
        fetch(`${BASE_URL}/next`).then(
            res => {
                return res.json();
            }
        ).then(data => {
            let temp = [{weight: data["start_weight"]}, {weight: data["end_weight"]}]
            console.log(data)
            this.setState({
                imgMeta: data,
                imageSrc: `${BASE_URL}/img/${data["id"]}`,
                crop: {x: 0, y: 0},
                zoom: 1,
                cropMeta: temp
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
        crops[this.state.currCrop] = this.cropper.getData()
        this.setState({
            cropData: crops
        });
    }

    onIndexChange(e){
        console.log(e)
    }
    render() {
        return (

            <div className="App">
                <Grid columns='two' divided>

                    <Grid.Column width={4}>
                        {this.state.cropMeta.map((d, idx) => <CropGallery callback={this.onIndexChange} key={idx + "img"}
                                                                          index={idx} meta={d}
                                                                          info={this.state.cropData[idx]}/>)}
                    </Grid.Column>
                    <Grid.Column width={8}>

                        <div>
                            <Cropper
                                style={{height: 400, width: '100%'}}
                                guides={false}
                                src={this.state.imageSrc}
                                ref={cropper => {
                                    this.cropper = cropper;
                                }}
                            />
                        </div>
                        <div>
                            <div className="box" style={{width: '50%', float: 'right'}}>
                                <button onClick={this.cropImage} style={{float: 'right'}}>
                                    Crop Image
                                </button>


                            </div>
                        </div>
                        <br style={{clear: 'both'}}/>
                    </Grid.Column>
                </Grid>

            </div>
        )
    }
}

const rootElement = document.getElementById('root')
ReactDOM.render(<App/>, rootElement)
