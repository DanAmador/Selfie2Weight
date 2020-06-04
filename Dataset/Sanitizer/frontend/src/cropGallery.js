import React from 'react';

import {Card, Grid, Image, Input, Button} from 'semantic-ui-react'


class CropGallery extends React.Component {
    state = {
        meta: {}
    }

    constructor(props) {
        super(props);
        this.onChange = this.onChange.bind(this)
        this.convertFreedomUnits = this.convertFreedomUnits.bind(this)
        this.state = {
            imgUrl: null,
            data: this.props.info,
            selected: false,
            index: this.props.index,
            meta: null,
            toPound: true
        }
    }

    convertFreedomUnits(override = false) {
        if (this.state.data || override) {
            let {weight} = this.state.data;
            let tp = this.state.toPound || override;
            let constant = tp ? 0.453592 : 2.20462;
            this.setState({data: {weight: (weight * constant).toFixed(3)}, toPound: !tp})
        }
    }

    onChange(e, d) {
        let copy = this.state.data;
        copy[d["label"]] = d["value"];
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
                  style={{minWidth: 300}}>
                <Card.Content>
                    <Card.Meta><span>Index: {this.state.index}</span></Card.Meta>

                    <Grid rows={2}>
                        <Grid.Row>
                            {Object.keys(this.state.data).filter(k => k !== "id").map((key, idx) =>
                                <Grid.Column key={"cropGaller_Input_" + idx}>
                                    <Input label={key}
                                           type={"number"}
                                           onChange={this.onChange}
                                           labelPosition='left'
                                           value={this.state.data[key]}
                                    />
                                </Grid.Column>
                            )}
                        </Grid.Row>

                        <Grid.Row>
                            <Grid.Column>
                                <Button
                                    onClick={this.convertFreedomUnits}>{this.state.toPound ? "To Lbs" : "To KG"}</Button>
                                <Image src={this.state.imgUrl} fluid rounded style={{maxHeight: 200}}/>
                            </Grid.Column>
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
