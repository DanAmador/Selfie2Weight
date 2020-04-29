import React from 'react';

import {Card, Grid, Image, Input} from 'semantic-ui-react'


class CropGallery extends React.Component {
    state = {
        meta: {}
    }

    constructor(props) {
        super(props);
        this.onChange = this.onChange.bind(this)
        this.state = {
            imgUrl: null,
            data: this.props.info,
            selected: false,
            index: this.props.index,
            meta: null
        }
    }

    onChange(e, d) {
        let copy = this.state.data
        copy[d["label"]] = d["value"]
        this.setState({
            data: copy
        })
    }


    setColor() {
        return this.state.selected ? "red" : "black"
    }

    render() {
        return (

            <Card onClick={e => this.props.indexChangeCallback(this.state.index)} color={this.setColor()}
                  style={{minWidth: 100}}>
                <Card.Content as="button">
                    <Card.Meta><span>Index: {this.state.index}</span></Card.Meta>

                    <Grid rows={2}>


                            {Object.keys(this.state.data).filter(k => k !== "id").map((key, idx) =>

                                <Input label={key}
                                       key={"cropGaller_Input_" + idx}
                                       onChange={this.onChange}
                                       labelPosition='right corner'
                                       value={this.state.data[key]}
                                       fluid
                                />
                            )}


                        <Grid.Row>
                            <Image src={this.state.imgUrl} fluid rounded style={{maxHeight: 200}}/>

                        </Grid.Row>
                    </Grid>

                </Card.Content>
                {/*TODO Work on this */}
                {/*<Button basic color='red' onClick={e => this.props.deleteCallback(this)}>*/}
                {/*    Delete*/}
                {/*</Button>*/}
            </Card>
        )
    }

}

export default CropGallery;
