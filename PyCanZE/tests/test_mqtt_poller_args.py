import sys
import types

# Stub paho.mqtt.client before importing mqtt_poller
mqtt_client_stub = types.SimpleNamespace(Client=lambda *args, **kwargs: None)
paho = types.ModuleType("paho")
mqtt_mod = types.ModuleType("mqtt")
mqtt_mod.client = mqtt_client_stub
paho.mqtt = mqtt_mod
sys.modules.setdefault("paho", paho)
sys.modules["paho.mqtt"] = mqtt_mod
sys.modules["paho.mqtt.client"] = mqtt_client_stub

from pycanze import mqtt_poller


def test_env_defaults(monkeypatch):
    monkeypatch.setenv("PYCANZE_HOST", "1.2.3.4")
    monkeypatch.setenv("PYCANZE_PORT", "36000")
    monkeypatch.setenv("MQTT_HOST", "mqtt.local")
    monkeypatch.setenv("MQTT_PORT", "2883")
    monkeypatch.setenv("MQTT_TOPIC", "test/topic")
    monkeypatch.setenv("PYCANZE_VEHICLE", "ZOE")
    monkeypatch.setattr(sys, "argv", ["mqtt_poller"])
    args = mqtt_poller.parse_args()
    assert args.host == "1.2.3.4"
    assert args.port == 36000
    assert args.mqtt_host == "mqtt.local"
    assert args.mqtt_port == 2883
    assert args.mqtt_topic == "test/topic"
    assert args.vehicle == "ZOE"
    assert args.interval == 300


def test_cli_overrides_env(monkeypatch, tmp_path):
    monkeypatch.setenv("PYCANZE_HOST", "ignored")
    csv = tmp_path / "out.csv"
    db = tmp_path / "out.db"
    argv = [
        "mqtt_poller",
        "--host",
        "9.8.7.6",
        "--port",
        "1234",
        "--mqtt-host",
        "cli.example",
        "--mqtt-port",
        "4321",
        "--mqtt-topic",
        "cli/topic",
        "--vehicle",
        "Twingo",
        "--interval",
        "42",
        "--log-csv",
        str(csv),
        "--log-sqlite",
        str(db),
        "--log-rotate",
        "99",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    args = mqtt_poller.parse_args()
    assert args.host == "9.8.7.6"
    assert args.port == 1234
    assert args.mqtt_host == "cli.example"
    assert args.mqtt_port == 4321
    assert args.mqtt_topic == "cli/topic"
    assert args.vehicle == "Twingo"
    assert args.interval == 42
    assert args.log_csv == csv
    assert args.log_sqlite == db
    assert args.log_rotate == 99


def test_config_file(monkeypatch, tmp_path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        """
interval: 10
mqtt_host: cfg.example
mqtt_topic: cfg/topic
fields:
  - a
  - b
log_csv: metrics.csv
"""
    )
    monkeypatch.setattr(sys, "argv", ["mqtt_poller", "--config", str(cfg)])
    args = mqtt_poller.parse_args()
    assert args.interval == 10
    assert args.mqtt_host == "cfg.example"
    assert args.mqtt_topic == "cfg/topic"
    assert args.fields == ["a", "b"]
    assert args.log_csv == cfg.parent / "metrics.csv"
    monkeypatch.setattr(
        sys, "argv", ["mqtt_poller", "--config", str(cfg), "--interval", "20"]
    )
    args = mqtt_poller.parse_args()
    assert args.interval == 20
