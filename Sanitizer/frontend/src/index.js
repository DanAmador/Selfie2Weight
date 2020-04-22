import React from 'react'
import ReactDOM from 'react-dom'
import './styles.css'
import Cropper from 'react-cropper';

import 'cropperjs/dist/cropper.css'; // see installation section above for versions of NPM older than 3.0.0
import CropGallery from "./cropGallery"
import {Grid, Card, Header} from 'semantic-ui-react'
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';


const cropper = React.createRef(null);
const BASE_URL = "http://127.0.0.1:5000"

class App extends React.Component {
    componentDidMount() {
        this.onNext();
    }

    state = {
        imageSrc: null,
        crop: {x: 0, y: 0},
        zoom: 1,
        croppedAreaPixels: null,
        croppedImage: null,
        isCropping: false,
        currCrop: 0,
        imgMeta: null,
        imgId: "",
        data: []
    }

    constructor(props) {
        super(props);
        this.cropImage = this.cropImage.bind(this);
        this.onNext = this.onNext.bind(this);
        this.onNextGallery = this.onNextGallery.bind(this);
        this.onIndexChange = this.onIndexChange.bind(this);
        this.onAddGallery = this.onAddGallery.bind(this);
        this.onSave = this.onSave.bind(this);
        this.galleryRefs = []
        this.setGalleryRefs = element => {
            this.galleryRefs.push(element)
        }

    }

    onSave() {
        let data = []
        this.galleryRefs.forEach(r => {
            let meta = r.state.meta;
            if (meta && r.state.saved) {
                data.push({
                    meta: r.state.meta,
                    data: r.state.data
                })
            }
        })

        if (data.length !== 0) {
            const requestOptions = {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            };

            fetch(`${BASE_URL}/img/${this.state.imgId}`, requestOptions)
                .then(response => response.json())
                .then(r => this.processRequest(r));
        } else {
            toast('🦄 Crop list is empty 🦄', {
                position: "bottom-left",
                autoClose: 5000,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
            });

        }
    }

    onNextGallery() {
        this.onIndexChange((this.state.currCrop + 1) % this.galleryRefs.length)
    }

    onAddGallery() {
        let t = Object.assign({}, this.state.data[0])
        let copy = this.state.data
        copy.push(t)
        this.setState({
            data: copy
        })
    }

    processRequest(data) {
        {
            let temp = [{weight: data["start_weight"]}, {weight: data["end_weight"]}]
            delete data["start_weight"]
            delete data["end_weight"]
            temp = temp.map(t => {

                return Object.assign(t, data)

            })
            this.setState({
                imgId: data["id"],
                imageSrc: `${BASE_URL}/img/${data["id"]}`,
                zoom: 1,
                data: temp
            })

            while (this.galleryRefs.length !== 2) {
                this.galleryRefs.pop()
            }
            this.galleryRefs.map((gal, idx) => {
                let canvas = this.cropper.getCroppedCanvas()
                gal.setState({
                    imgUrl: canvas === null ? "" : canvas.toDataURL(),
                    saved: false,
                    data: temp[idx]
                })
            })

        }
    }

    onNext(e) {
        fetch(`${BASE_URL}/next`).then(
            res => {
                return res.json();
            }
        ).then(data => this.processRequest(data))
    }

    cropImage() {
        if (typeof this.cropper.getCroppedCanvas() === 'undefined') {
            return;
        }


        let affectedGallery = this.galleryRefs[this.state.currCrop]
        let meta = this.cropper.getData()
        affectedGallery.setState({
            imgUrl: this.cropper.getCroppedCanvas(meta).toDataURL(),
            meta: meta,
            saved: true
        })
    }

    onIndexChange(index) {
        let e = this.galleryRefs[index]
        this.setState({
            currCrop: index
        })
        this.cropper.setData(e.state.meta)

    }

    getCurrentInfo() {
        if (this.state.data.length !== 0) {
            return <p>Index: {this.state.currCrop} <b>
                {this.state.data[this.state.currCrop]["weight"]} kg</b>
            </p>

        }
        return ""
    }

    render() {
        return (

            <div className="App">
                <ToastContainer
                    position="top-right"
                    autoClose={5000}
                    hideProgressBar={false}
                    newestOnTop={false}
                    closeOnClick
                    rtl={false}
                    pauseOnFocusLoss
                    draggable
                    pauseOnHover
                /> <Header> {this.getCurrentInfo()}</Header>
                <Grid rows={2} divided>
                    <Grid.Row width={8}>

                        <Cropper
                            style={{height: 400, width: '100%'}}
                            guides={true}
                            src={this.state.imageSrc}
                            viewMode={2}
                            ref={cropper => {
                                this.cropper = cropper;
                            }}
                        />
                        <div>
                            <div className="box" style={{width: '50%', float: 'right'}}>
                                <button onClick={this.cropImage} style={{float: 'right'}}>
                                    Crop Image
                                </button>

                                <button onClick={this.onAddGallery} style={{float: 'right'}}>
                                    NUU GALLERY
                                </button>
                                <button onClick={this.onNextGallery} style={{float: 'right'}}>
                                    next
                                </button>


                                <button onClick={this.onSave} style={{float: 'right'}}>
                                    to server
                                </button>
                            </div>
                        </div>
                        <br style={{clear: 'both'}}/>
                    </Grid.Row>
                    <Grid.Row width={4}>
                        <Card.Group itemsPerRow={3}>
                            {this.state.data.map((data, idx) =>
                                <CropGallery callback={this.onIndexChange}
                                             key={idx + "_imgViewer"}
                                             ref={this.setGalleryRefs}
                                             index={idx}
                                             info={data}/>
                            )}
                        </Card.Group>

                    </Grid.Row>

                </Grid>

            </div>
        )
    }
}

const rootElement = document.getElementById('root')
ReactDOM.render(<App/>, rootElement)
