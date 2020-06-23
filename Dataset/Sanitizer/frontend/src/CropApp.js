import React from 'react'
import './styles.css'
import Cropper from 'react-cropper';

import 'cropperjs/dist/cropper.css'; // see installation section above for versions of NPM older than 3.0.0
import CropGallery from "./cropGallery"
import {
    Button,
    ButtonContent,
    Dropdown, Grid,
    Header,
    Icon,
    Label,
    List,
    Message,
    Popup,
    Segment
} from 'semantic-ui-react'
import {toast, ToastContainer} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import {GlobalHotKeys} from "react-hotkeys";
import Responsive from "semantic-ui-react/dist/commonjs/addons/Responsive";
import {instanceOf} from 'prop-types';
import {withCookies, Cookies} from 'react-cookie';
import Form from "semantic-ui-react/dist/commonjs/collections/Form";
// const BASE_URL = `http://${window.location.hostname}:5000`;
const BASE_URL = "http://192.168.0.115:5000";


class App extends React.Component {

    static propTypes = {
        cookies: instanceOf(Cookies).isRequired
    };

    componentDidMount() {
        this.setState({
            name: this.props.cookies.get("name") || "Dan"
        });
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
        data: []

    }

    keyMap = {
        DELETE: 'q',
        SUBMIT: 's',
        NEW_GALLERY: 'z',
        CHANGE_INDEX: [" ", "SpaceBar", ""],
        REMOVE_FREEDOM: 'x'
    };
    handlers = {
        NEW_GALLERY: e => this.onAddGallery(),
        REMOVE_FREEDOM: e => this.onLbsConvert(),
        DELETE: e => this.onSendEmpty(),
        SUBMIT: e => this.onSave(),
        CHANGE_INDEX: e => this.onNextGallery(),
    };

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
        this.onLbsConvert = this.onLbsConvert.bind(this);
        this.handleNameChange = this.handleNameChange.bind(this);

        this.galleryRefs = []
        this.setGalleryRefs = element => {
            this.galleryRefs.push(element)
        }


    }

    handleNameChange(event) {
        const {cookies} = this.props;
        const name = event.target.value;
        cookies.set('name', name, {path: '/'});
        this.setState({"name": name});
    }

    postToServer(data, showToast = true) {
        const requestOptions = {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        };
        let empty = Object.keys(data).length === 0;
        console.log(`${BASE_URL}/img/${this.state.imgMeta["reddit_id"]}?name=${this.state.name}`)
        console.log(requestOptions)
        try {
            fetch(`${BASE_URL}/img/${this.state.imgMeta["reddit_id"]}?name=${this.state.name}`, requestOptions)
                .then(response => {
                    if (response.status === 201 || response.status === 200) {
                        if (showToast)
                            this.showToast(empty ? "Deleted succesfully ✂️" : "Successfully saved 💾💾")
                    }
                })
        } catch (error) {
            console.log(error)
        }

    }

    onSave() {
        let data = []
        this.galleryRefs.forEach(r => {
            let meta = r.state.meta;
            if (meta && r.state.imgUrl !== "") {
                data.push({
                    meta: r.state.meta,
                    data: r.state.data
                })
            }
        })

        if (data.length !== 0) {
            // console.table(data)
            this.postToServer(data,)
            this.onNext()
        } else {
            this.showToast('🦄 Crop list is empty 🦄');
        }
    }

    //Mark as "sanitized" to ignore or 'delete' image
    onSendEmpty(showToast = true) {
        this.postToServer({}, showToast);
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


    async processRequest(data) {
        // console.table(data)

        let {age} = data;
        let temp = [{weight: data["start_weight"], age: age}, {weight: data["end_weight"], age: age}]
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

        this.refs.cropper.replace(img_url)


        while (this.galleryRefs.length !== 2) {
            this.galleryRefs.pop()
        }

        this.galleryRefs.forEach((gal, idx) => {
            let canvas = this.refs.cropper.getCroppedCanvas()
            gal.setState({
                imgUrl: canvas === null ? "" : canvas.toDataURL(),
                data: temp[idx],
                selected: idx === this.state.currCrop,
                toPound: false
            })
        })

        return true

    }

    async onNext() {
        fetch(`${BASE_URL}/next`)
            .then(
                res => {
                    if (res.status === 400) {
                        return Promise.reject()
                    }
                    if (res.status === 404 || res.status === 500) {
                        return Promise.reject(new Error("bad_image"))
                    }
                    return res.json();
                })
            .then(data => {
                return this.processRequest(data)
            })
            .catch(error => {
                this.showToast("Deleted image, loading next");
                return false
            });


    }


    cropImage() {
        if (typeof this.refs.cropper.getCroppedCanvas() === 'undefined') {
            return;
        }


        let affectedGallery = this.galleryRefs[this.state.currCrop]
        let meta = this.refs.cropper.getData()
        affectedGallery.setState({
            imgUrl: this.refs.cropper.getCroppedCanvas(meta).toDataURL(),
            meta: meta,
        })
        // this.onIndexChange((this.state.currCrop + 1) % this.galleryRefs.length)

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
            this.refs.cropper.setData(e.state.meta)

        }
    }


    onLbsConvert() {
        this.galleryRefs.forEach(r => {
            r.convertFreedomUnits()
        });
    }

    onGalleryDelete(gallery) {
        let length = this.state.data.length;
        let index = gallery.state.index;
        if (this.galleryRefs && index <= length && length > 2) {
            let newData = this.state.data;

            newData.splice(index, 1)

            let newIdx = (index + 1) % this.galleryRefs.length;
            // this.galleryRefs = this.galleryRefs.filter(e => e !== null && e !== gallery).map((e, idx) => {
            //     e.setState({
            //         index: idx,
            //         selected: newIdx === idx
            //     })
            //     return e;
            // })

            if (this.state.currCrop === index) {
                this.setState({data: newData, currCrop: newIdx})
            } else {
                this.setState({data: newData})

            }
        }

    }

    getCurrentInfo() {
        if (this.state.data.length !== 0) {
            let {age, sex, height, reddit_id, title} = this.state.imgMeta;
            let data = {
                title: title,
                age: age,
                sex: sex,
                height: height,
                id: reddit_id,
                index: this.state.currCrop,
                weight: this.state.data[this.state.currCrop]["weight"],
            };
            let icons = {
                age: "calendar alternate outline",
                sex: "transgender",
                height: "text height",
                id: "reddit alien",
                index: "magic",
                weight: "frown outline",
                title: "book"
            }

            let items = Object.entries(data).map((entry, idx) => {
                let k = entry[0];
                let v = entry[1];

                return <Popup key={`list_popup_info_${idx}`} content={k}
                              trigger={<List.Item as='a' key={`list_gallery_info_${idx}`}>
                                  <Icon name={icons[k]}/>
                                  <List.Content>

                                      <List.Description>
                                          {k === "title" ? <Label> {v}</Label> : v}
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
                <GlobalHotKeys keyMap={this.keyMap} handlers={this.handlers}/>

                <ToastContainer position="top-right" autoClose={5000} hideProgressBar={false} newestOnTop={false}
                                closeOnClick rtl={false} pauseOnFocusLoss draggable pauseOnHover/>
                <Grid column={2} divided>

                    <Grid.Column width={8}>
                        <Responsive as={Segment}>


                            <Header> {this.getCurrentInfo()}</Header>

                            <Cropper
                                style={{minHeight: 500, maxHeight: 700, minWidth: 300, maxWidth: 700}}
                                guides={true}
                                src={this.state.imageSrc}
                                viewMode={2}
                                responsive={true}
                                ref={'cropper'}
                                cropend={this.cropImage}
                            />
                        </Responsive>

                        <Grid.Row columns={3}>
                            <Grid.Column>
                                <Responsive as={Button.Group}>

                                    <Button primary animated onClick={this.onSendEmpty} style={{float: 'right'}}>

                                        <ButtonContent visible> Delete Image</ButtonContent>
                                        <ButtonContent hidden> {this.keyMap.DELETE}</ButtonContent>
                                    </Button>
                                    <Button animated primary onClick={this.onSave} style={{float: 'right'}}>
                                        <ButtonContent visible> Post</ButtonContent>
                                        <ButtonContent hidden> {this.keyMap.SUBMIT}</ButtonContent>
                                    </Button>
                                </Responsive>
                            </Grid.Column>
                            <Grid.Column>
                                <Responsive as={Button.Group}>

                                    <Button animated onClick={this.onAddGallery} style={{float: 'right'}}>
                                        <ButtonContent visible> Extra Weight</ButtonContent>
                                        <ButtonContent hidden> {this.keyMap.NEW_GALLERY}</ButtonContent>
                                    </Button>


                                    <Button animated onClick={this.onNextGallery}
                                            style={{float: 'right'}}>
                                        <ButtonContent visible> Next</ButtonContent>
                                        <ButtonContent hidden> {this.keyMap.CHANGE_INDEX}</ButtonContent>
                                    </Button>


                                    <Button animated onClick={this.onLbsConvert}
                                            style={{float: 'right'}}>
                                        <ButtonContent visible> Convert Units</ButtonContent>
                                        <ButtonContent hidden> {this.keyMap.REMOVE_FREEDOM}</ButtonContent>
                                    </Button>
                                    <Dropdown text='Guidelines' icon='question circle outline' floating labeled button
                                              className='icon'>
                                        <Dropdown.Menu>
                                            <Message
                                                icon='inbox'
                                                header='Guidelines'
                                                list={["Face must be present", "Skip shitty pictures", "No freedom units",
                                                    "Try to maintain single person per image", "Adjust age"]}
                                            />
                                        </Dropdown.Menu>
                                    </Dropdown>
                                    <Form>
                                        <Form.Input
                                            placeholder={this.state.name}
                                            name='name'
                                            onChange={this.handleNameChange}
                                        />
                                    </Form>
                                </Responsive>
                            </Grid.Column>

                        </Grid.Row>
                    </Grid.Column>
                    <Grid.Column width={8} rows={3}>

                        {this.state.data.map((data, idx) =>
                            <CropGallery indexChangeCallback={this.onIndexChange}
                                         deleteCallback={this.onGalleryDelete}
                                         key={idx + "_imgViewer"}
                                         ref={this.setGalleryRefs}
                                         index={idx}
                                         info={data}/>
                        )}

                    </Grid.Column>

                </Grid>
            </div>
        )
    }

}

export default withCookies(App)