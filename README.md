```
python3 -m venv venv
source venv/bin/activate
cd rust_bindings
maturin build --release
pip install target/wheels/*.whl

add encrypted sqlite
```

