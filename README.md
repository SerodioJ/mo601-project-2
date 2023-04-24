# Simulador simples do procesador RISC-V - MO601 1s/2023

## João Alberto Moreira Seródio - 218548

## Instruções para build e execução

Execute na raiz do repostório o comando abaixo para construir a imagem Docker (uma imagem com o toolkit já compilado é utilizada como imagem base)

```
docker build -t mo601-p2-218548 .
```

Para executar as simulações para todos os testes na pasta `test` utilize

```
docker run --rm -v ./test:/simulator/test mo601-p2-218548:latest python3 cli.py -p "/simulator/test/*.c" -c
```
