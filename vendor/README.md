# Preserved Upload Source Material

This directory preserves recoverable source material from both user-supplied archive sets without deleting, flattening, or silently replacing files.

## Boundaries

`source-sets/first` contains the recoverable trees and recovery indexes reconstructed from the first upload set. `source-sets/second` contains the recoverable trees and recovery indexes reconstructed from the second upload set. The same upstream appearing in both sets remains in both locations so the archive-set provenance is not lost.

The source trees retain their original README files, licenses, notices, Dockerfiles, YAML, package manifests, configuration, tests, fixtures, and runtime metadata. Only regenerable caches, dependency installations, Git metadata, and build output were excluded from the preservation copies; those are not source files from the uploads and would create non-reproducible noise.

## Integration boundary

David AI is the single control plane. The maintainable David application imports only the small Fabric adapter and orchestration contracts from these sources. Mixed Python, Node, browser, CUDA, GPU, database, and workflow runtimes remain bounded services or workers and are not merged into David’s base dependency graph.

Incomplete archives and split fragments remain under recovery indexes or recovery artifacts and are marked unavailable in the capability registry. They are not treated as executable merely because a partial source tree exists.

See `../docs/intelligence-fabric/UPLOAD-PRESERVATION-MANIFEST.md` for checksums and the exact preservation policy. See `../docs/intelligence-fabric/FULL-CAPABILITY-DIRECTIVE.txt` for the governing user requirements.
