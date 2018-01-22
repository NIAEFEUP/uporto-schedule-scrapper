module.exports = (sequelize, DataTypes) => {
  return sequelize.define('faculty', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true
    },
    acronym: {
      type: DataTypes.STRING
    },
    name: {
      type: DataTypes.STRING
    },
  }, {
    tableName: 'faculty',
    underscored: true,
    timestamps: false
  });
};
