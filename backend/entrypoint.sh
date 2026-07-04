#!/bin/sh
set -e

SRC_KUBECONFIG="${KUBECONFIG_SOURCE:-/root/.kube/config}"
DEST_DIR="/root/.kube-writable"
DEST_KUBECONFIG="$DEST_DIR/config"

mkdir -p "$DEST_DIR"

if [ -f "$SRC_KUBECONFIG" ]; then
  cp "$SRC_KUBECONFIG" "$DEST_KUBECONFIG"
  chmod 600 "$DEST_KUBECONFIG"

  # Rewrite kind cluster server addresses (127.0.0.1:<host-port>) to the
  # in-network control-plane container so this container can reach them.
  # kind names contexts/clusters "kind-<name>" and the container
  # "<name>-control-plane" on the "kind" docker network.
  python3 - "$DEST_KUBECONFIG" <<'EOF'
import sys, yaml

path = sys.argv[1]
with open(path) as f:
    config = yaml.safe_load(f)

for cluster_entry in config.get("clusters", []):
    name = cluster_entry.get("name", "")
    if name.startswith("kind-"):
        node_name = name[len("kind-"):] + "-control-plane"
        cluster_entry["cluster"]["server"] = f"https://{node_name}:6443"

with open(path, "w") as f:
    yaml.safe_dump(config, f)
EOF

  export KUBECONFIG="$DEST_KUBECONFIG"
fi

exec "$@"
