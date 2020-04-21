import React from 'react';

import {Card, Image} from 'semantic-ui-react'


class CropGallery extends React.Component {


    constructor(props) {
        super(props);

    }

    getMeta(o) {
        let m = []
        for (let key in o) {
            m.push(<p key={key + "gallery"}><b>{key}:</b> {o[key]}</p>);
        }
        return m
    }

    render() {
        return (
            <Card as="button" onClick={e => this.props.callback(this.props.index)}>
                <Image src={this.props.imgUrl} wrapped ui={false}/>
                <Card.Content>
                    <Card.Meta>
                        {this.getMeta(this.props.infonfo)}
                    </Card.Meta>

                    <Card.Description>


                    </Card.Description>

                    <Card.Content extra>
                        <a>
                            {this.getMeta(this.props.meta)}

                        </a>
                    </Card.Content>
                </Card.Content>

            </Card>
        )
    }
}

export default CropGallery;
