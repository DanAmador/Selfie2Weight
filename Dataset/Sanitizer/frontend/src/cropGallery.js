import React from 'react';

import {Card, Image, Input, Grid} from 'semantic-ui-react'


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
            saved: false
        }
    }

    onChange(e, d) {
        let copy = this.state.data
        copy[d["label"]] = d["value"]
        this.setState({
            data: copy
        })
    }

    render() {
        return (

            <Card as="button" onClick={e => this.props.callback(this.props.index)}>
                <Card.Content>
                <Card.Meta><span>Index: {this.props.index}</span></Card.Meta>

                    <Grid rows={2}>


                        <Grid.Row columns={3} centered>
                            {Object.keys(this.state.data).filter(k => k != "id").map((key, idx) =>

                                <Input label={key}
                                       key={"cropGaller_Input_" + idx}
                                       onChange={this.onChange}
                                       labelPosition='right corner'
                                       value={this.state.data[key]}
                                       size={"small"}/>
                            )}
                        </Grid.Row>
                        <Grid.Row>
                            <Image src={this.state.imgUrl} fluid rounded style={{maxHeight: 200}}/>

                        </Grid.Row>
                    </Grid>

                </Card.Content>

            </Card>
        )
    }
}

export default CropGallery;
