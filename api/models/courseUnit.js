module.exports = (sequelize, DataTypes) => {
    return sequelize.define('courseUnit', {
        course_unit_id: {
            type: DataTypes.INTEGER
        },
        course_id: {
            type: DataTypes.INTEGER
        },
        name: {
            type: DataTypes.STRING
        },
        acronym: {
            type: DataTypes.STRING
        },
        url: {
            type: DataTypes.STRING(2000)
        },
        schedule_url: {
            type: DataTypes.STRING(2000)
        },
    }, {
        tableName: 'course_unit',
        underscored: true,
        timestamps: false,

    });
}