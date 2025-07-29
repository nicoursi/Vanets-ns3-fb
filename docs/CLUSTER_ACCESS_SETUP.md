# Setting Up Access to Cluster Submit Hosts

## 1. Configure ProxyJump in `~/.ssh/config`

Edit (or create) `~/.ssh/config` on your local machine:

```sshconfig
Host clusterlabta
    HostName labsrv0.math.unipd.it
    User username
    ProxyJump username@labta.math.unipd.it
    ServerAliveInterval 30
    ServerAliveCountMax 60
```

**Explanation:**

* `Host clusterlabta` → an alias you will use for SSH/SFTP.
* `HostName` → the actual internal host (target) you want to reach. 
* `User` → your username on the target.
* `ProxyJump` → the jump/bastion host you must connect through.

**Alternative servers**
Sometimes some of the servers could be down. Here the list of all servers available:

1. Department hosts to connect through:

    - labta.math.unipd.it
    - sshtorre.math.unipd.it
2. Submit hosts:

    - labsrv0.math.unipd.it (New! Please give it a try and report)
    - labsrv7.math.unipd.it
    - labsrv8.math.unipd.it

**Connect with:**

```bash
ssh clusterlabta
sftp clusterlabta
```

It will automatically jump through `labta.math.unipd.it` to `labsrv0.math.unipd.it`.

---

## 2. Set up SSH key-based auth for both hosts

* Generate SSH keys locally (if you don’t have them):

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

When asked **“Enter file in which to save the key”**, just press **Enter** to use the default (`~/.ssh/id_ed25519`).

> **Note:** You don’t use the server password to *generate* a key. The key is created locally and never needs the server’s password. You only use your password **once** when you copy the public key to the server with `ssh-copy-id`. After that, even if the server password changes, your key-based login will still work.

* Copy the key to the server (you will need your password this one time):

```bash
ssh-copy-id clusterlabta
```

After this, you can SSH, SFTP, or mount with SSHFS without typing a password every time.

---

## 3. Mount the remote host with SSHFS

Install `sshfs` if you don't have it:

```bash
sudo apt install sshfs
```

Create a local mount point:

```bash
mkdir -p ~/cluster_mount
```

Mount the remote host:

```bash
sshfs clusterlabta:/ ~/cluster_mount
```

Now `~/cluster_mount` acts like a normal folder, but everything inside is actually on the remote host.

**When done, unmount with:**

```bash
fusermount -u ~/cluster_mount
```

---

## 4. Create aliases locally
It can be useful to create aliases for commands you need often by editing the `~/.bash_aliases` file on your system.

Example:

```
alias mount-cluster='sshfs -o loglevel=debug clusterlabta://storage/username ~/cluster_mount'
alias umount-cluster='fusermount -u ~/cluster_mount'
```

## 5. Sourcing aliases on the cluster submit hosts:
I maintain a cluster-specific `.bashrc` file containing useful aliases for this project.
To ensure it gets sourced automatically, run the following script on one of the cluster submit hosts:

```
build-env/source_aliases_on_cluster.sh
```
