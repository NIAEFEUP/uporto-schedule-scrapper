module.exports = (sequelize, DataTypes) => {
    return sequelize.define('class', {
        year: {
            type: DataTypes.INTEGER
        },
        acronym: {
            type: DataTypes.STRING
        },
        url: {
            type: DataTypes.STRING(2000)
        },
        course_id: {
            type: DataTypes.INTEGER
        },
    }, {
        tableName: 'class',
        underscored: true,
        timestamps: false
    });
}