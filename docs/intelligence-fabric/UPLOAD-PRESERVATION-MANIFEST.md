# Upload Preservation Manifest

This manifest records every uploaded archive and split fragment supplied across the first and second upload sets. Recoverable source trees are preserved under `vendor/source-sets/first` and `vendor/source-sets/second`; recovery indexes and readable archive artifacts are preserved under those same boundaries. Regenerable caches and build outputs are not source material and are excluded.

## Uploaded file checksums

```text
f20ea879c5b4e95d604add2230065f406ae1ac709dd60db5b7c17df7a6a9d7b4  /home/ubuntu/upload/David-AI-Intelligence-Fabric-Core.zip
6d2a772395cb2e4e78135e6fd7ec8dcef0ca7e3e7a25dafa58b000575f22f9b6  /home/ubuntu/upload/David-Sources-Pack-1-2.zip
d514fcd29e9e2a9b52cdd03219337a6d6422a259aa389349d6c21513728690e6  /home/ubuntu/upload/David-Sources-Pack-1.zip
dde659c9d9aefdfb35c48ea9e00c956575ea7d7443093204566051ef12f45fc2  /home/ubuntu/upload/David-Sources-Pack-2-1.zip
9c1e5994b45cdff7331d91a11189618e83cd1c43cd840e845e9682018c3e3b17  /home/ubuntu/upload/David-Sources-Pack-2-2.zip
6d803dadcd321f4e48f8b25afbd76794c8bea1f3cb34151e8e0f1f9e3af4c4c7  /home/ubuntu/upload/David-Sources-Pack-2-3.zip
90ac08fbda5329b32ea30f896849f22fad18ce7cc818b7228867c86a2d864269  /home/ubuntu/upload/David-Sources-Pack-2-4.zip
565bd5a5852297902844cb27d605789770582d3d77483a84309bc8db67ac48fa  /home/ubuntu/upload/David-Sources-Pack-2-5.zip
3986ab6c5209b5ea4691ef286465d8e7ff23fdd129c8fee1dacf20b01c12ea77  /home/ubuntu/upload/David-Sources-Pack-2.zip
4536389f94d50d67c05c6452c12da748eb40cdbe98cce3287299eb2b7de7eef9  /home/ubuntu/upload/David-Sources-Pack-3-1.zip
b43ede874843b586f29f3e5fca6d22806fc0382c9efcbbbdea15811151d82aab  /home/ubuntu/upload/David-Sources-Pack-3-2.zip
25579c6c23f7c1024eebba64bfa4c7e5371c1e494b6dcf2df063443b4f1c8a61  /home/ubuntu/upload/David-Sources-Pack-3.zip
39c707f8bea55bcdb8e7b17c821889d6d96776d9d758bcd83a9ceaee2611b9f7  /home/ubuntu/upload/David-Sources-Pack-4.zip
6d10720cb72e93659748a51ad10b3a36387b58b057588dfb9576d61b4c5e4f89  /home/ubuntu/upload/DavidAI-backend-with-voice.zip-1.part-aa
fb505501fde1120550db4930433cf937d8434d61442d5ff61c167326f691b81d  /home/ubuntu/upload/DavidAI-backend-with-voice.zip-1.part-ab
1b12bdd3fb90a7b7a884de78b064667f2fc5072d76968117749e6a4091f6ad22  /home/ubuntu/upload/DavidAI-backend-with-voice.zip.part-aa
ae6d485c77e3154b15cd7b9dabf83c5a648dbdc9fbf8cf827a0b58da8ce48d66  /home/ubuntu/upload/DavidAI-backend-with-voice.zip.part-ab
0b3575f83e277838926cd3efdab568fe4b6fe7bb356eb134fde5be4cbdd6853f  /home/ubuntu/upload/pasted_content.txt
```

## Preservation policy

- Existing David code and APIs remain in place.
- The first and second recoverable source sets are preserved separately under `vendor/source-sets`.
- Upstream licenses, notices, YAML, Docker, package, and runtime files remain with their source trees.
- Incomplete archive fragments are recorded as recovery artifacts and are never reported as executable capabilities.
- No source tree was deleted because of integration difficulty; unavailable dependencies are represented by controlled service boundaries.
