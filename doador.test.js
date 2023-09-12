const Doador = require('./doador');
const Usuario = require('./usuario')

test('deve criar um doador com os valores corretos', () => {
  const doador = new Doador('Giovana', 'giovanabruno@email.com', 'Sorocaba', 'Curativo A');
  expect(doador.getNome()).toBe('Giovana');
  expect(doador.getContato()).toBe('giovanabruno@email.com');
  expect(doador.getTipo()).toBe('Doador');
  expect(doador.getRegiao()).toBe('Sorocaba');
  expect(doador.getTipoCurativo()).toBe('Curativo A');
});