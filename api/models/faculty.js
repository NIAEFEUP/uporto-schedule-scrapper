module.exports = (sequelize, DataTypes) => {
  var faculty = sequelize.define('faculty', {
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

  faculty.associate = function(models) {
    console.log("models: " + models);
    models.faculty.hasMany(models.course);
  };

  return faculty;
};