import React from 'react'
import ReactDOM from 'react-dom'
import './styles.css'
import Cropper from 'react-cropper';

import 'cropperjs/dist/cropper.css'; // see installation section above for versions of NPM older than 3.0.0
import CropGallery from "./cropGallery"
import {Grid, Card, Header, List, Icon, Popup} from 'semantic-ui-react'
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import {HotKeys} from "react-hotkeys";

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
        data: [],


    }

    constructor(props) {
        super(props);
        this.cropImage = this.cropImage.bind(this);
        this.onNext = this.onNext.bind(this);
        this.onNextGallery = this.onNextGallery.bind(this);
        this.onIndexChange = this.onIndexChange.bind(this);
        this.onAddGallery = this.onAddGallery.bind(this);
        this.onSave = this.onSave.bind(this);
        this.onGalleryDelete = this.onGalleryDelete.bind(this);
        this.showToast = this.showToast.bind(this);
        this.onSendEmpty = this.onSendEmpty.bind(this);
        this.galleryRefs = []
        this.setGalleryRefs = element => {
            this.galleryRefs.push(element)
        }
    }

    postToServer(data) {
        const requestOptions = {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        };

        fetch(`${BASE_URL}/img/${this.state.imgMeta["reddit_id"]}`, requestOptions)
            .then(response => {
                console.log(response)
                if (response.status === 201 || response.status === 200) {
                    this.showToast("Successfully saved 💾💾")
                }
            })
    }

    onSave() {
        let data = []
        this.galleryRefs.forEach(r => {
            let meta = r.state.meta;
            if (meta) {
                data.push({
                    meta: r.state.meta,
                    data: r.state.data
                })
            }
        })

        console.table(data)
        if (data.length !== 0) {
            this.postToServer(data,)
            this.onNext()
        } else {
            this.showToast('🦄 Crop list is empty 🦄');
        }
    }

    //Mark as "sanitized" to ignore or 'delete' image
    onSendEmpty() {
        this.postToServer({});
        this.onNext();
    }

    onNextGallery() {
        this.onIndexChange((this.state.currCrop + 1) % this.galleryRefs.length)
    }

    showToast(text) {
        toast(text, {
            position: "bottom-left",
            autoClose: 2000,
            hideProgressBar: false,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
        });

    }

    onAddGallery() {
        let t = Object.assign({}, this.state.data[0])
        let copy = this.state.data
        copy.push(t)
        this.setState({
            data: copy
        })
        console.table(this.galleryRefs)

    }

    processRequest(data) {
        console.log("in process request")
        console.table(data)
        let temp = [{weight: data["start_weight"]}, {weight: data["end_weight"]}]
        let {reddit_id} = data

        let img_url = `${BASE_URL}/img/${reddit_id}`
        console.log(img_url)
        this.setState({
            imgId: reddit_id,
            imageSrc: img_url,
            zoom: 1,
            data: temp,
            currCrop: 0,
            imgMeta: data
        })

        this.cropper.replace(img_url)
        while (this.galleryRefs.length !== 2) {
            this.galleryRefs.pop()
        }

        this.galleryRefs.forEach((gal, idx) => {
            let canvas = this.cropper.getCroppedCanvas()
            gal.setState({
                imgUrl: canvas === null ? "" : canvas.toDataURL(),
                data: temp[idx],
                selected: idx === this.state.currCrop,
            })
        })


    }

    async onNext() {
        fetch(`${BASE_URL}/next`)
            .then(
                res => {
                    console.log(res)
                    if (res.status === 400) {
                        return Promise.reject()
                    }
                    if (res.status === 404) {
                        return Promise.reject(new Error("bad_image"))
                    }
                    return res.json();
                })
            .then(data => this.processRequest(data))
            .catch(error => {
                this.showToast("Deleted image, loading next");

            });
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
        this.onIndexChange((this.state.currCrop + 1) % this.galleryRefs.length)

    }

    onIndexChange(index) {
        if (typeof this.galleryRefs[index] !== "undefined") {

            let e = this.galleryRefs[index]
            this.galleryRefs[this.state.currCrop].setState({
                selected: false
            })
            this.setState({
                currCrop: index
            })
            e.setState({
                selected: true
            })
            this.cropper.setData(e.state.meta)

        }
    }

    onGalleryDelete(gallery) {
        let length = this.state.data.length;
        let index = gallery.state.index;
        if (this.galleryRefs && index <= length && length > 2) {
            let newData = this.state.data;

            console.table(newData)
            newData.splice(index, 1)
            console.table(newData)

            let newIdx = (index + 1) % this.galleryRefs.length;
            // this.galleryRefs = this.galleryRefs.filter(e => e !== null && e !== gallery).map((e, idx) => {
            //     e.setState({
            //         index: idx,
            //         selected: newIdx === idx
            //     })
            //     return e;
            // })
            console.table(this.galleryRefs)

            if (this.state.currCrop === index) {
                this.setState({data: newData, currCrop: newIdx})
            } else {
                this.setState({data: newData})

            }
        }

    }

    getCurrentInfo() {
        if (this.state.data.length !== 0) {
            let {age, sex, height, reddit_id} = this.state.imgMeta;
            let data = {
                age: age,
                sex: sex,
                height: height,
                id: reddit_id,
                index: this.state.currCrop,
                weight: this.state.data[this.state.currCrop]["weight"]
            };
            let icons = {
                age: "calendar alternate outline",
                sex: "transgender",
                height: "text height",
                id: "reddit alien",
                index: "magic",
                weight: "frown outline"
            }

            let items = Object.entries(data).map((entry, idx) => {
                let k = entry[0];
                let v = entry[1];

                return <Popup key={`list_popup_info_${idx}`} content={k}
                              trigger={<List.Item as='a' key={`list_gallery_info_${idx}`}>
                                  <Icon name={icons[k]}/>
                                  <List.Content>

                                      <List.Description>
                                          {v}
                                      </List.Description>
                                  </List.Content>
                              </List.Item>}/>


            });
            return <List horizontal key={"list_gallery"}>{items}</List>
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

                                <button onClick={this.onSendEmpty} style={{float: 'right'}}>
                                    delete image
                                </button>


                                <button onClick={this.onSave} style={{float: 'right'}}>
                                    to server
                                </button>
                            </div>
                        </div>
                        <br style={{clear: 'both'}}/>
                    </Grid.Row>
                    <Grid.Row>
                        <Card.Group itemsPerRow={3}>
                            {this.state.data.map((data, idx) =>
                                <CropGallery indexChangeCallback={this.onIndexChange}
                                             deleteCallback={this.onGalleryDelete}
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

const
    rootElement = document.getElementById('root')
ReactDOM
    .render(
        <App/>,
        rootElement
    )
