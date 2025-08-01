## Legal Notice
This project is provided under the [Apache License 2.0](./LICENSE). See the [NOTICE](./NOTICE) file for usage disclaimers and ethical guidelines. Use responsibly.

⚠️ These tools are provided for educational and authorized‑testing purposes only. Do not run them against systems you do not own or have explicit written permission to test. The author is not liable for misuse.

# WirePatrol
AI-powered anomaly detection plugin for Wireshark, designed to identify suspicious network activity in real time. This tool continuosly monitor netwrok traffic and detects threads in real-time, adapts to each website's behavior, and operates under MLOps principles.

Continuos operation:
* Since every website is unique, the user interaction model must be tailored to the individual traffic on that site. To solve this problem, a complete artificial intelligence system is needed that uses MLOps principles to automate processes as much as possible (cyclical training, testing, etc.).

* Tshark is used in the background to enable the plugin to work efficiently.

The ultimate goal will be to make completly autonomous system that can evolve and adapt for any website with optional user system or model tuning.

### Initial Training data
We use pentest scripts, whose presence forces the appearance of attack-specific packets. This data is also marked with markers signaling the start (START) and end (END) of the attack. Between attacks, there are episodes of normal traffic (INTERVALs).

#### Raw data recording
On a server which hosting website during pentesting the following capture_attack.sh should be executed:

sudo ./capture_packets.sh Wirepatrol </path/to/output>

Saved files should be placed in /Data/raw directory


#### Set of features - 21.07.25
packet_number
– Sequential index of the packet within the capture (as assigned by Wireshark).
– Useful for ordering or referring back to the original packet.

timestamp
– The absolute time when the packet was sniffed (a datetime).
– Basis for computing true inter‑arrival times and correlating with external logs.

delta_time
– The time in seconds since the previous packet in the DataFrame (true inter‑arrival).
– After sorting by timestamp, .diff() gives you real gaps, so you can spot bursts vs. idle periods.

layer
– Highest protocol layer detected (e.g. TCP, TLS, HTTP, DNS, UDP).
– Helps you filter or group by protocol in downstream processing.

Ethernet fields

eth_src, eth_dst
• Source and destination MAC addresses. Great for spotting spoofing or strange interface hops.

IP fields

ip_src, ip_dst
• Source and destination IPv4 addresses.

ip_ttl
• The IP time‑to‑live—drops in TTL can reveal network path length or odd TTL manipulations.

ip_id
• The IP identification field, useful for detecting packet‑fragmentation patterns or ID reuse.

frame_len
– Total packet length on the wire (bytes), including headers.
– Good for detecting jumbo frames, tiny ACK‑only packets, or oddly large control packets.

TCP fields

tcp_srcport, tcp_dstport
• The source and destination TCP ports (e.g. 443 → your HTTPS server).

Flags (tcp_syn, tcp_ack, tcp_fin, tcp_rst, tcp_psh, tcp_urg)
• Each is 0/1, indicating whether that TCP flag was set. Patterns of these flags reveal handshakes, resets, pushes, etc.

tcp_seq, tcp_acknum
• Sequence and acknowledgment numbers; by differencing them you can infer retransmissions or out‑of‑order segments.

tcp_window_size
• The advertised window size, showing receiver buffer capacity and flow‑control changes.

tcp_payload_len
• The raw TCP payload length (after the TCP header). Often zero for handshake packets.

TLS fields

tls_record_len
• Length of the encrypted TLS record (bytes). Key side‑channel feature even when payload is opaque.

tls_version
• TLS record version (e.g. 1.2 or 1.3), useful for detecting downgrade attacks.

tls_handshake_type
• Type code of handshake messages (e.g. 1 for ClientHello, 11 for Certificate).

tls_ciphersuite
• Negotiated cipher suite string, a fingerprint of server configuration.

tls_sni
• The Server Name Indication (hostname) sent in clear during ClientHello—shows which virtual host you’re hitting.

HTTP fields

http_method
• HTTP request method (e.g. GET, POST).

http_uri
• The request‑URI (path + query) — useful for spotting long injection payloads or scanning patterns.

http_response_code
• The server’s response code (e.g. 200, 401, 404, 500).

DNS fields

dns_qry_name
• The queried domain name (for DNS requests).

dns_a
• The A‑record answer (if present).

dns_txt
• Any TXT‑record data—helps detect exfil over DNS.

With this schema, each row is a rich snapshot of everything Wireshark can see at each packet:

Link‑layer (Ethernet) → network‑layer (IP) → transport‑layer (TCP/UDP) → session‑layer (TLS/HTTP/DNS)

Timing: both absolute (timestamp) and relative (delta_time)

Side‑channels: TLS record sizes, HTTP URI lengths, DNS query patterns

Control: TCP flags and window sizes

### Model
Since it often happens that during attacks, normal traffic appears among anomalous traffic, we cannot focus on anomalies during attacks (between START and END). The model should focus on learning the distribution of normal traffic and reject out-of-distribution data that are likely to be attacks. For that task I will test many autoencoder types (DAE, VAE, normal autoencoder)

1) Train an autoencoder on the clean training dataset.

2) Deploy alongside the main model, as a shadow model.

3) Add Open-set rejection layer to your inference pipeline.

4) Create alerting logic:

    * AE reconstruction loss > threshold

    * OSR rejection rate > expected

5) Feed anomalies to a retraining or human-in-the-loop system.

6) Log all drift signals to MLFlow or Prometheus/Grafana dashboards.


### Installation
To run scripts you need Tshark installed for example with:
```bash
sudo apt install tshark
```

### Project structure:
```
/wirepatrol/ 
├── Data/                        # Raw, interim, and processed datasets
│   ├── raw/                     # Original data, raw json files extracted from 
│   ├── processed/                # Preprocessed datasets - csv files with extracted and selected features
│
├── notebooks/                    # Jupyter notebooks for experimentation, data exploration and also preprocessing. It is also a good place for feature engineering/selection and saving to files, so it could be later automated in e.g. cross-validation.
│
├── src/                          # ML source code
│   ├── __init__.py
│   ├── data/                     # Data loading, preprocessing, pentesting scripts
│   ├── models/                   # Model architectures, semi-supervised autoencoder and other anomaly detection architectures
│   ├── training/                 # Training logic, trainers, schedulers
│   ├── evaluation/               # Evaluation metrics, confusion matrices
│   ├── serving/                  # ONNX export helpers, inference sanity tests
│   ├── utils/                    # Helper functions, common code like paths.py - to standarize paths
│   ├── cli.py                    # CLI entrypoint (train, export, evaluate)
│   ├── config.yaml               # Hyperparameters, architecture selection, parameters for pentesting scripts
│
├── experiments/                   # MLFlow tracking runs
│   ├── mlruns/                    # MLFlow local run storage
│   └── tracking.db                # (optional) Local SQLite DB for MLFlow
│
├── outputs/                        # All model outputs & artifacts
│   ├── checkpoints/                # Exported ONNX or PyTorch models
│   ├── logs/                       # Training logs, console outputs
│   ├── predictions/                # Inference outputs (optional) like comparison of actual labels (attack markers) with model predictions, reconstruction error, etc.
│   └── figures/                    # Evaluation plots
│
├── tests/                          # All tests - they will be performed by CI/CD (e.g., Github actions)
│   ├── unit/                       # Unit tests for data, models, training (test_data_loading.py, test_preprocessing.py, test_model.py, test_training.py, test_evaluation.py, test_data_distribution.py, test_feature_importance_stability.py)
│   ├── integration/                # Test for inference and practical usage for example time during real-time inference (test_packet_processing.c, test_inference.c, test_plugin_integration.c)
│   ├── monitoring/                 # Test data/concept drift (because I want ask users to send inference data, this part can be done localy only) 
│
├── scripts/                        # DevOps & automation scripts
│   ├── capture_packets.sh          # Used to gather data druing pentesting
│
├── deployment/                      # Deployment & CI/CD infra
│   ├── infrastructure/              # Infra and pipeline configs
│   │   ├── github-actions/          # GitHub Actions YAML workflows
│   │   │   ├── ml_pipeline.yml      # ML training + model deployment
│   │   ├── gitlab-ci/               # (Optional) GitLab CI pipeline configs
│   ├── docker/                      # Dockerfiles for training / testing
│
├── logs/                            # Local dev logs (optional gitignored)
├── inference                       # entire logic for program that is using our trained model
│   ├── src
│   │   ├── plugin.c
│   │   ├── inference.c
│   │   ├── model_loader.c
│   │   ├── packets_processing.c
│   │   ├── config.c 
│   ├── CMakeLists.txt
│   ├── Dockerfile 		    # to build Wireshark with plugin and compile in consistent environment
│
├── .env                             # MLFlow URI, API keys, secrets
├── requirements.txt / pyproject.toml # Python dependencies
├── MLproject                         # MLFlow entrypoint for reproducible runs
└── README.md
```

Explanation of tests files:
Python Files:
These files are typically used for unit testing the higher-level functionality of your machine learning pipeline, data preprocessing, and model training, so they should remain in Python:

* test_data_loading.py: Tests for loading data, ensuring the correct parsing of json files, CSV files, or any other data format. Since this interacts with data pipelines and machine learning preprocessing, it’s best to keep it in Python.

* test_preprocessing.py: Tests for preprocessing scripts or transformations applied to data (e.g., normalization, feature extraction). This should also be in Python since it is closely related to the data science pipeline.

* test_model.py: Tests for model instantiation, training loops, model loading, etc. This should stay in Python because it’s related to ML model logic (e.g., PyTorch, TensorFlow, or ONNX-based models).

* test_training.py: Tests related to the training process such as loss functions, optimization, and checkpointing. This file is best written in Python since it directly interacts with the model training code and the ML framework.

* test_evaluation.py: Tests that evaluate model performance (e.g., accuracy, precision, recall). This can include confusion matrix computation or metrics like AUC. Keep this in Python because it will likely involve high-level Python libraries like sklearn, matplotlib, or pandas.

* test_data_distribution.py: Tests that ensure your data distribution is correct (e.g., class balance in your dataset). This is also best handled in Python, especially if you’re using Python libraries to process and visualize your data (e.g., pandas, matplotlib, seaborn).

* test_feature_importance_stability.py: Tests related to feature importance and model stability (e.g., using SHAP or permutation importance). This is likely to rely on Python-based ML libraries for analysis, so it should remain in Python.

C Files:
Now, regarding the C files, the Wireshark plugin and inference logic are critical for interacting with ONNX models and Wireshark. You will need to write C unit tests and integration tests for the plugin itself.

* test_inference.c: Unit tests specifically related to inference with the model using ONNX Runtime and how it processes packet data. This should be written in C because it’s directly testing the low-level logic of how the model is being run in C (via ONNX Runtime).

* test_plugin_integration.c: This would test the integration of the Wireshark plugin, ensuring it works correctly within the Wireshark environment, interacts with packet data, and triggers inference. Again, this should be in C because it’s directly testing the functionality of the plugin, which is written in C.

* test_packet_processing.c: Tests related to processing packet data, which is likely written in C as well. You would need to ensure that packets are processed correctly and are ready for model inference.

Integration of Tests:
Python tests would be used for testing the high-level machine learning workflows and data pipeline components, like data loading, preprocessing, model evaluation, etc.

C tests would be used for testing lower-level functionality like the Wireshark plugin and the inference process, which require direct interaction with the plugin and ONNX Runtime.

# Data pipeline
```
                       ┌────────────────────┐
                       │  Raw Input Data    │
                       └──────── ┬──────────┘
                                 │
                                 ▼
               ┌────────────────────────────────────┐
               │    Preprocessing (shared logic)    │
               └─────────────────┬──────────────────┘
                                 │
           ┌─────────────────────┴─────────────────────┐
           │                                           │
           ▼                                           ▼
┌────────────────────────┐          ┌──────────────────────────────────────┐
│ Protobuf Serialization │          │ Relational database for versioning   │
│ (.proto schema)        │          │ and to store data with drift metrics │
└──────────┬─────────────┘          └──────────────────┬───────────────────┘
           │                                           │
           ▼                                           ▼
   ┌────────────────┐                      ┌───────────────────────┐
   │ Model Training │◄──────Retrain────────┤ Data Drift Monitoring │
   └───────┬────────┘                      └───────────────────────┘
           │                                           ▲
           │                                           │
           ▼                                       Logs/Stats
  ┌─────────────────┐                                  │
  │ Model Inference │◄───────Input & Prediction────────┘
  └─────────────────┘

```
Copy of data is stored in database to monitor drfit and trigger automatic retraining. Given that here we got Cybersecurity task model has to be retrained frequently. We can also approach this differently by adding a reinforcement learning component to online learning support.
We could also introduce anchor dataset for stability - static representative dataset to deal with false confidence 


# Explanation of plugin compilation
To clarify how you compile and build your Wireshark plugin, here's a step-by-step overview of the proper build process. You essentially compile the plugin as part of the Wireshark build process, not in isolation. The plugin needs to interact with Wireshark’s internal libraries, so it must be compiled alongside Wireshark itself.

### Wireshark Compilation Environment
To build a Wireshark plugin, you need a Wireshark development environment. This is where you compile Wireshark itself, and as part of that process, you also compile the plugin into the Wireshark binary.

#### Typical Steps for Compilation:
1. Install Wireshark Development Dependencies:
You need the Wireshark source code and its development libraries (headers, linking libraries, etc.) for the plugin to be able to access Wireshark’s core API. Although we will use Tshark compliation process is the same:

Example inside docker container:

```bash
sudo apt-get install libwireshark-dev
```
2. Get the Wireshark Source Code:
You can either download a stable release of the Wireshark source code from the official website or clone the repository from Git:

```bash
git clone https://gitlab.com/wireshark/wireshark.git
cd wireshark
```

3. Write the Wireshark Plugin Code:
Your plugin’s C code will interact with the Wireshark API. For example, it might register new dissectors, process packets, etc. You write the code for the plugin, typically in a directory like /wireshark/plugins/myplugin.

4. Build Wireshark:
Now you will compile Wireshark and your plugin together. You do this by configuring the build system with CMake or ./configure, depending on your platform.

If using CMake, the typical steps look like this:

```bash
mkdir build
cd build
cmake ..
make
```

Important: When you run make, Wireshark will be compiled, and any plugins (including your custom plugin) will also be compiled and linked with Wireshark. The plugin code is processed during the build.

5. Plugin Integration:
When you build Wireshark, it will automatically load your plugin as long as it’s placed in the appropriate plugin directory and compiled correctly. Wireshark dynamically loads the plugin at runtime when you launch the Wireshark GUI.

We can only compile plugin when it is inside Wireshark repository folder (or pointed to it)
Docker container will be place when all of that compilation and building will take place.

##### Dockerfile example:
```Dockerfile
# Start with a base image that supports development tools (Ubuntu as an example)
FROM ubuntu:20.04

# Install dependencies (e.g., Wireshark, build tools, ONNX Runtime, etc.)
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    cmake \
    git \
    libpcap-dev \
    libwireshark-dev \
    wget \
    libssl-dev \
    pkg-config \
    python3-pip \
    libboost-all-dev

# Install Wireshark (or clone from the repository). For reporduction we could get specific version
RUN git clone --branch master https://gitlab.com/wireshark/wireshark.git /wireshark
WORKDIR /wireshark

# Install required libraries and dependencies for Wireshark
RUN ./autogen.sh && \
    ./configure && \
    make -j$(nproc) && \
    make install

# Clone your plugin repository or copy the plugin code
WORKDIR /wireshark/plugins/myplugin
COPY ./myplugin/ .  # Assuming the plugin is in your local project directory

# Set up the plugin compilation using CMake
WORKDIR /wireshark
RUN cmake . && \
    make myplugin

# Set up entrypoint to run the Wireshark application (if needed)
CMD ["/usr/local/bin/wireshark"]
```

##### Model update logic
1) Inference of current version is monitored and saving sampled data to postgres database for data/concept drift. 
2) If drift is detected, we train a new model. 
3) If it got better performance and AUC values in comparison to previous ones, automatic deployment is triggered to staging, new container is created. Wireshark with new model is recompiled and testing begins (Shadow testing). 
4) If in production environment model works better than previous version, there is automatic switch of versions with minimal downtime.


### System and plugin usage
Since the plugin is designed to run from the command line and in the background to detect anomalies, its monitoring and alerting UI will be web-based (web GUI). 

Docker-compose.yml orchestrate containers for training (in python using pytorch), inference (C plugin), staging (for A/B or Shadow testing), postgres (work with data/concept drift detection), Grafna, Prometheus and FastAPI (web GUI monitoring, and alerting system if anomaly is detected)


