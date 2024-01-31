#/bin/sh

CONFIG_FILE="program_qspi.ini"
GUI=
PRODUCT_ID=
echo cwd: `pwd`
which zenity > /dev/null
[ $? -eq 0 ] && GUI=y

#### Dump old config section

dump_config_text() {
       echo Existing Configuration
       echo ----------------------
       echo "PRODUCT_ID: $PRODUCT_ID"
       echo ----------------------
}

dump_config() {
        eval $(cat $CONFIG_FILE)
        if [ -z "$GUI" ] ; then
                dump_config_text
                ask_change
        else
                zenity --question --title "QSPI programming" --text="`dump_config_text 2>&1`" --ok-label "Change" --cancel-label "Keep"
                if [ $? -ne 0 ] ; then
                        exit 0
                fi
        fi
}

ask_change() {
        echo -n "Change existing configuration (y/N or [ENTER] for n)? "
        read ans
        case $ans in
        Y) return
                ;;
        y) return
                ;;
        *) echo Keeping old config
                exit 0
        esac
}

# Get chip revision section
get_prod_id() {
	if [ -z "$GUI" ] ; then
		PRODUCT_ID=
		while : ; do
			echo "Product id options:"
			echo "0:  DA14680/1-01"
			echo "1:  DA14682/3-00, DA15XXX-00 (default)"
			echo -n "Product id ? (0..1 or [ENTER] for 1)"
			read ans
			case $ans in
			0) PRODUCT_ID="DA14681-01"
				;;
			1) PRODUCT_ID="DA14683-00"
				;;
			"") PRODUCT_ID="DA14683-00"
				;;
			*) echo ; echo "Invalid chip revision. Try again " ; echo
			esac
			[ -z "$PRODUCT_ID" ] || break
		done
	else
		while : ; do
			PRODUCT_ID=`zenity --separator=':' --list --column "Product Id" --title="Select Product Id" DA14680/1-01 DA14682/3-00`
			[ $? -eq 0 ] && PRODUCT_ID=`echo $PRODUCT_ID | cut -d ':' -f1 | sed -e 's/[0-9]\///'` && echo $PRODUCT_ID && break
		done
	
	fi
}


if [ -f $CONFIG_FILE ] ; then
        dump_config
fi


get_prod_id


echo "export PRODUCT_ID=\"$PRODUCT_ID\"" > $CONFIG_FILE
