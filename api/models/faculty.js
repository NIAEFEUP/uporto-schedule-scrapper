module.exports = (sequelize, DataTypes) => {
  return sequelize.define('faculty', {
    acronym: {
      type: DataTypes.STRING,
    },
    name: {
      type: DataTypes.STRING,
    },
  }, {
    tableName: 'faculty',
    underscored: true,
    timestamps: false,
  });
};
