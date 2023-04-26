# Simulador simples do procesador RISC-V - MO601 1s/2023

## João Alberto Moreira Seródio - 218548

## Instruções para build e execução

Execute na raiz do repostório o comando abaixo para construir a imagem Docker (uma imagem com o toolkit já compilado é utilizada como imagem base)

```
docker build -t mo601-p2-218548 .
```

Para executar as simulações para todos os testes (\*.riscv) na pasta `test` utilize

```
docker run --rm -v ${PWD}:/simulator mo601-p2-218548:latest python3 project/cli.py
```

É possível executar o simulador sem utilizar a imagem docker, mas pode ser necessário utilizar a flag -t caso o prefixo da toolchain do RISC-V não seja `riscv32-unknown-elf`, como no exemplo abaixo
```
python3 project/cli.py -t riscv64-linux-gnu
```

### Comparação de logs com o Spike Sim

Execute as simulações com a flag -s, isso faz com que o código seja compilado com a flag `-static` e também remove o disassembly do log da instrução

```
docker run --rm -v ${PWD}:/simulator mo601-p2-218548:latest python3 project/cli.py -s
```

Gere os logs do spike com os arquivos compilados, para isso os scripts `generate_logs.py` e `merge_logs.py` na pasta `spike` podem ser utilizados.

```
docker run --rm -v ${PWD}:/simulator mo601-p2-218548:latest python3 spike/generate_logs.py
```

```
docker run --rm -v ${PWD}:/simulator mo601-p2-218548:latest python3 spike/merge_logs.py
```

A comparação pode ser feita com o script `cmp_logs.py` na raiz do repositório.

```
docker run --rm -v ${PWD}:/simulator mo601-p2-218548:latest python3 cmp_logs.py
```
