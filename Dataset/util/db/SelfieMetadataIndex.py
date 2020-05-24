class SelfieMetadataIndex:
    @staticmethod
    def create_index(es, name):
        if not es.index.exists(index=name):
            index_body = {
                "settings": {
                    "number_of_shards": 5,
                    "number_of_replicas": 1
                },
                "mappings": {
                    "properties": {
                        "has_been_sanitized": {"type": "boolean"},
                        "title": {"type": "text"},
                        "sex": {"type": "keyword"},
                        "age": {"type": "integer"},
                        "start_weight": {"type": "float"},
                        "end_weight": {"type": "float"},
                        "local_path": {"type": "text"},
                        "img_url": {"type": "text"},
                        "reddit_id": {"type": "text"},
                        "sanitized": {"type": "nested"},
                        "meta_data": {"type: nested"}
                    }
                }
            }

            es.indes.create(index=name, body=index_body)
