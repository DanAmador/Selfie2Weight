import React from 'react';

import {Card, Grid, Image, Input, Button} from 'semantic-ui-react'
import Responsive from "semantic-ui-react/dist/commonjs/addons/Responsive";


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

    convertFreedomUnits() {
        if (this.state.data) {
            let {weight} = this.state.data;
            let copy = this.state.data;
            let tp = this.state.toPound;
            let constant = tp ? 0.453592 : 2.20462;
            copy["weight"] = (weight * constant).toFixed(3);
            this.setState({data: copy, toPound: !tp})
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

            <Responsive as={Card} onClick={e => this.props.indexChangeCallback(this.state.index)}
                        color={this.setColor()}
                        style={{minWidth: 300}}>
                <Card.Content>
                    <Card.Meta><span>Index: {this.state.index}</span></Card.Meta>

                    <Grid rows={2}>
                        <Responsive as={Grid.Column}>
                            {Object.keys(this.state.data).filter(k => k !== "id").map((key, idx) =>
                                <Grid.Row key={"cropGaller_Input_" + idx}>
                                    <Input label={key}
                                           type={"number"}
                                           onChange={this.onChange}
                                           labelPosition='left'
                                           value={this.state.data[key]}
                                    />
                                </Grid.Row>
                            )}
                        </Responsive>

                        <Grid.Row>
                            <Grid.Column>
                                <Button
                                    onClick={this.convertFreedomUnits}>{this.state.toPound ? "To Lbs" : "To KG"}</Button>
                                <Image src={this.state.imgUrl} fluid rounded style={{maxHeight: 200}}/>
                            </Grid.Column>
                        </Grid.Row>
                    </Grid>

                </Card.Content>
                {/*TODO Work on this */
                }
                {/*<Button basic color='red' onClick={e => this.props.deleteCallback(this)}>*/
                }
                {/*    Delete*/
                }
                {/*</Button>*/
                }
            </Responsive>
        )
    }

}

export default CropGallery;
