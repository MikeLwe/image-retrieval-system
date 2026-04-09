# Image Retrieval System
### Using natural language to lookup images based on the image's content

## Design
#### CLI-interface
- Controls if the user is trying to upload or request an image
- Listens to user input and update from the database service
- Broadcasts the user input

#### Upload
- Listens to the file pathways
- Broadcasts the raw image content

#### Image Process
- Pair an image with the
- Listens to the incoming raw image content from the Upload
- Broadcasts that the image information has been processed (this will be a couple of vertices/coordinates on the image along with a label saying all of the boxes the image has)

#### Document DB Service
- Stores information relating to an image
- Listens to the Image Process and takes in the position information and labels, pairing it to the image
- Broadcasts that the content of the image has been saved (for the CLI Interface)

#### Embedding Service
- Converts information into a vector space
- Listens for image content to be stored (from Image Process) OR user input asking to retrieve something
- Broadcasts that the content has been embedded

#### Vector Index Service
- Stores vector embedding
- Listens for the Embedding Service, asking for the vectorized information of an image OR for the user input embedding to compare this embedding with existing ones
- Broadcasts that the content has been saved OR broadcasts information of vectors near the user input



