const Curativo = require('./curativo');

test('deve criar um curativo com o tipo correto', () => {
  const curativo = new Curativo('Micropor Anti alérgico');
  expect(curativo.tipo).toBe('Micropor Anti alérgico');
});
